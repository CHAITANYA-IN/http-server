#!/bin/python3
import os
import csv
import gzip
import zlib
from os import access, stat
import uuid
import random
import datetime
import time
import socket
import base64
import webbrowser
import threading

SERVER_NAME = "AMCHAT"
SERVER_VERSION = "0.0.1"
STATUS_CODE = {
    200: "OK",
    202: "Accepted",
    301: "Moved Permanently",
    304: "Not Modified",
    404: "Not Found",
    400: "Bad Request",
    500: "Internal Server Error",
    505: "HTTP Version Not Supported",
    201: "Created",
    204: "No Content",
    403: "Forbidden",
}

CONFIGURATION = {}
# Reading from amchat.conf to get the namelocation of the access and error log file
conf = open('amchat.conf', 'r')
CONFIGURATION = dict([i.split() for i in conf.read().split("\n")])
conf.close()

COOKIES = dict()
csvfile = open('cookies.log', 'r')
obj = csv.reader(csvfile)
for i in obj:
    if datetime.datetime.strptime(i[2], "%a, %d %b %Y %H:%M:%S %Z") > datetime.datetime.now():
        COOKIES[i[0]] = [i[1], i[2]]
csvfile.close()
csvfile = open('cookies.log', 'w')
obj = csv.writer(csvfile)
for i in COOKIES:
    obj.writerow([i, *COOKIES[i]])
csvfile.close()


def time_diff(stamp, path):
    """
        Last Modified Time IN YOUR DIRECTORY == If Modified Since FROM THE REQUEST
        13 Oct < 14 Oct = 304
        13 Oct >= 14 Oct = 200
    """
    a = datetime.datetime.strptime(time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(path))), '%Y-%m-%d %H:%M:%S')
    b = datetime.datetime.strptime(stamp, "%a, %d %b %Y %H:%M:%S %Z")

    return a < b


def timestamp(stamp=datetime.datetime.now(), offset=0):
    """
            function to give the expected time format in the response
            Mon Oct  5 22:18:48 2020 ---->  Mon, 27 Jul 2009 12:28:53 GMT
    """
    current_time = stamp
    current_time += datetime.timedelta(seconds=offset)
    current_time = current_time.ctime().split()

    return (current_time[0] + ", "
            + current_time[2] + " "
            + current_time[1] + " "
            + current_time[4] + " "
            + current_time[3] + " GMT")


def __body__(path, encoding=""):
    f = open(path, 'rb')
    if("gzip" in encoding):
        encoding = "gzip"
        data = gzip.compress(f.read())
    elif('deflate' in encoding):
        encoding = "deflate"
        data = zlib.compress(f.encode())
    else:
        encoding = ""
        data = f.read()
    f.close()
    return data, encoding


def get_handler(request_line, headers):
    """
    function to add data for response to GET request
    """
    data = ""
    encoding = ""
    path = ""
    if('www' in request_line[1]):
        status_code = 301
        return (status_code, '', '', '', '')
    else:
        if(request_line[1] == '/'):  # default file will be opened : "success.html"
            status_code = 200
            path = CONFIGURATION['DocumentRoot'] + '/success.html'
            if('If-Modified-Since' in headers):
                if(time_diff(headers['If-Modified-Since'], path)):
                    status_code = 304
            if os.access(path, os.R_OK):
                data, encoding = __body__(path, headers['Accept-Encoding'])
            else:
                status_code = 403
        # finding the relative file path
        elif(os.path.exists(CONFIGURATION['DocumentRoot'] + request_line[1])):

            status_code = 200
            path = CONFIGURATION['DocumentRoot'] + request_line[1]
            if('If-Modified-Since' in headers):
                if(time_diff(headers['If-Modified-Since'], path)):
                    status_code = 304
            if os.access(path, os.R_OK):
                data, encoding = __body__(path, headers['Accept-Encoding'])
            else:
                status_code = 403
        else:  # incase the file isnt found
            status_code = 404
            path = CONFIGURATION['DocumentRoot'] + "/error.html"
            data, encoding = __body__(path, headers['Accept-Encoding'])
            print(status_code, data, len(data), path.split(".")[-1], encoding)
        return (status_code, data, len(data), path.split(".")[-1], encoding)


def response_to_request(request):
    """
    In this function, request is broken and status_code,data,length is extracted from it.

    """
    status_code = 404
    response_h = ""
    response_body = ""
    cookie = ""
    access_log = ""
    error_log = ""
    form_data = ""
    length = None
    print("\n\n\nRequest:\n" + request)
    print("\n\n\n Response:\n")
    body = ""
    if('\r\n\r\n' in request):
        head, body = request.split("\r\n\r\n", 1)
    else:
        head = request
    head = head.split("\r\n")
    request_line = head[0]
    headers = head[1:]
    request_line = request_line.split()
    headers = dict([tuple([j.strip() for j in i.split(":", 1)])
                    for i in headers])
    if('Accept-Encoding' not in headers):
        headers['Accept-Encoding'] = ""
    cookie_exists = 'Cookie' in headers
    if (cookie_exists):
        cookies_in_request = [tuple(i.split("="))
                              for i in headers['Cookie'].split(";")]
        if(cookies_in_request[0] in COOKIES):
            pass
    else:
        cookie_name = uuid.uuid4().hex[:6].upper()
        cookie_value = random.randint(1173, 9999)
        expiration_date = str(timestamp(offset=2))
        COOKIES[cookie_name] = [cookie_value, expiration_date]
        csvfile = open('cookies.log', 'a+')
        obj = csv.writer(csvfile)
        obj.writerow((cookie_name, cookie_value, expiration_date))
        csvfile.close()
        cookie = "Set-Cookie: " + \
            str(cookie_name) + "=" + str(cookie_value) + \
            "; Expires=" + expiration_date + '\r\n'

    try:
        if(request_line[2] != "HTTP/1.1"):
            status_code = 505
            response_h = "HTTP/1.1 " + \
                str(status_code) + " " + STATUS_CODE[status_code] + '\r\n\r\n'
            response_h += cookie

        elif(request_line[0] == "GET"):
            status_code, data, length, ext, encoding = get_handler(
                request_line, headers)
            response_h = "HTTP/1.1 " + str(status_code) + " "
            response_h += STATUS_CODE[status_code] + "\n"
            response_h += "Date: " + timestamp() + "\n"
            # check last modified only if the file exists
            response_h += "Server: " + SERVER_NAME + "/" + SERVER_VERSION + "\n"
            response_h += cookie
            if(status_code == 301):
                response_h += 'Location: '
                if('https://' not in request_line[1]):
                    response_h += 'https://'
                if('www' not in request_line[1]):
                    response_h += 'www.'
                response_h += request_line[1][1:] + '\r\n\r\n'
            else:
                if(os.path.exists(CONFIGURATION['DocumentRoot'] + request_line[1])):
                    response_h += "Last-Modified: " + timestamp(stamp=datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                        os.path.getmtime(CONFIGURATION['DocumentRoot'] + request_line[1]))), '%Y-%m-%d %H:%M:%S')) + "\n"
                if(encoding != ""):
                    response_h += 'Content-Encoding: ' + encoding + ' \r\n'
                response_h += "Content-Length: " + str(length)
                if(ext in ['png', 'jpg', 'bmp', 'jpeg']):
                    response_h += "\nContent-Type: image/" + ext + "\r\n\r\n"
                elif(ext == 'ico'):
                    response_h += "\nContent-Type: image/vnd.microsoft.icon" + "\r\n\r\n"
                else:
                    response_h += "\nContent-Type: text/" + ext + "\r\n\r\n"
                if(status_code != 304):
                    response_body = data

        elif(request_line[0] == "POST"):
            index = request_line[1].find('?')
            status_code = 200
            response_h = "HTTP/1.1 " + str(status_code) + " "
            response_h += STATUS_CODE[status_code] + "\n"
            response_h += "Date: " + timestamp() + "\n"
            response_h += "Server: " + SERVER_NAME + "/" + SERVER_VERSION + "\n\r\n"
            if('Content-Type' in headers):
                if(headers['Content-Type'] == 'application/x-www-form-urlencoded'):
                    form_data = [tuple([j for j in i.split("=")]) for i in body[:int(
                        headers['Content-Length']) + 1].split("&")]
                elif(headers['Content-Type'] == 'multipart/form-data'):
                    pass
                else:
                    pass
            if(index == -1):
                path = request_line[1]
            else:
                path = request_line[1][:index]
            if(path == "/"):
                response_h += open("." + path + 'success.html').read()
            else:
                response_h += open("." + path).read()

        elif(request_line[0] == "PUT"):
            new_str = CONFIGURATION['DocumentRoot'] + request_line[1]
            if not os.path.exists(new_str):
                status_code = 201
                f = open(new_str, "w")
                f.write(body)
                f.close()
            else:
                status_code = 204
                if(os.access(new_str, os.W_OK)):
                    f = open(new_str, "w")
                    f.write(body)
                    f.close()
            response_h = "HTTP/1.1 {0} {1}\n".format(
                status_code, STATUS_CODE[status_code])
            response_h += cookie
            response_h += "Date: " + timestamp() + "\n"
            response_h += "Server: " + SERVER_NAME + "/" + SERVER_VERSION + "\n"
            response_h += "Content-Location: " + \
                str(os.path.abspath(new_str)) + '\r\n\r\n'

        elif(request_line[0] == "DELETE"):
            path = CONFIGURATION['DocumentRoot'] + request_line[1]
            if os.path.exists(path):
                f = open(path, 'r')
                response_body = f.read()
                th = threading.Thread(target=os.remove, args=(path,))
                th.start()
                status_code = 200
            else:
                status_code = 204
            response_h = f"HTTP/1.1 {status_code} {STATUS_CODE[status_code]}\n"
            response_h += "Date:" + timestamp() + "\n"
            response_h += "Server: " + SERVER_NAME + "/" + SERVER_VERSION + "\n"
            response_h += cookie + '\r\n'

        elif(request_line[0] == "HEAD"):

            status_code, data, length, ext, encoding = get_handler(
                request_line, headers)
            response_h = "HTTP/1.1 " + str(status_code) + " "
            response_h += STATUS_CODE[status_code] + "\n"
            response_h += "Date: " + timestamp() + "\n"
            # check if file exists before checking last modified
            if(os.path.exists(CONFIGURATION['DocumentRoot'] + request_line[1])):
                response_h += "Last-Modified: " + timestamp(stamp=datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                    os.path.getmtime(CONFIGURATION['DocumentRoot'] + request_line[1]))), '%Y-%m-%d %H:%M:%S')) + "\n"
            response_h += "Server: " + SERVER_NAME + "/" + SERVER_VERSION + "\n"
            response_h += cookie
            if(encoding != ""):
                response_h += 'Content-Encoding: ' + encoding + ' \r\n'
            response_h += "Content-Length: " + str(length)
            if(ext in ['png', 'jpg', 'bmp', 'jpeg']):
                response_h += "\nContent-Type: image/" + ext + "\r\n\r\n"
            elif(ext == 'ico'):
                response_h += "\nContent-Type: image/vnd.microsoft.icon" + "\r\n\r\n"
            else:
                response_h += "\nContent-Type: text/" + ext + "\r\n\r\n"
        else:
            raise Exception()

    except (socket.error, Exception) as e:
        print(f"Exception occurred:\n{e}")
        status_code = 400
        response_h = "HTTP/1.1 " + str(status_code) + " "
        response_h += STATUS_CODE[status_code] + "\n"
        response_h += "Date: " + timestamp() + "\n"
        response_h += "Server: " + SERVER_NAME + "/" + SERVER_VERSION + "\n\r\n"

    print(response_h)
    f = open(CONFIGURATION['DocumentRoot'] +
             CONFIGURATION['AccessLogFile'], "a+")
    access_log = headers['Host'].split(':')[0] + ' - -'
    access_log += datetime.datetime.now(
        datetime.timezone.utc).strftime(" [%d/%b/%Y:%H:%M:%S %z]")
    access_log += ' "{0}"'.format(head[0])
    access_log += ' ' + str(status_code)
    if(length != None):
        access_log += ' ' + str(length)
    else:
        access_log += ' "-"'
    if('User-Agent' in headers):
        access_log += ' {}'.format(headers['User-Agent'])
    if(cookie_exists):
        access_log += ' "' + headers['Cookie'] + '"'
    access_log += "\n"
    access_log += str(form_data)
    f.write(access_log)
    f.close()
    if(status_code != 404 and (status_code < 600 or status_code >= 400)):
        f = open(CONFIGURATION['DocumentRoot'] +
                 CONFIGURATION['ErrorLogFile'], "a+")
        error_log = datetime.datetime.now().strftime(
            " [%a %b %d %H:%M:%S.%f %Y]")
        error_log += " [error] [client " + headers['Host'].split(":")[0]
        error_log += ' ' + STATUS_CODE[status_code]
        error_log += ' ' + os.path.abspath(request_line[1][1:]) + '\n'
        f.write(error_log)
        f.close()
    print(response_body)
    if(type(response_body) != type(b'')):
        response_body = response_body.encode()
    keep_alive = {'timeout': 0,  'max': 0}
    if('Connection' in headers):
        if('Keep-Alive' in headers['Connection'] or 'keep-alive' in headers['Connection']):
            keep_alive = {
                'timeout': CONFIGURATION['MaxTimeout'], 'max': CONFIGURATION['MaxRequests']}
            if('Keep-Alive' in headers):
                keep_alive = dict([tuple([j.strip() for j in i.split("=")])
                                   for i in headers['Keep-Alive'].split(",")])
    return response_h.encode() + response_body, keep_alive.get('timeout'), keep_alive.get('max')
