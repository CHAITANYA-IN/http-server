#!/bin/python3

def not_modified(host, port, request_type):
    from requirement import timestamp
    not_modified_msg = f"""{request_type} /answer.txt HTTP/1.1\r
Connection: close\r
Host: 127.0.0.1:8888\r
If-Modified-Since: """ + timestamp(offset=2) + """\r
Cookie: afsd=4654\r
Cache-Control: max-age=0\r
Keep-Alive: timeout=5, max=3\r
Upgrade-Insecure-Requests: 1\r\n\r
"""  # 505
    import socket
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((host, port))
    r.send(not_modified_msg.encode())
    msg = r.recv(1024).decode()
    r.close()
    return msg


def version_error(host, port, request_type):
    version_error_msg = f"""{request_type} /answer.txt HTTP/2.0\r
Connection: close\r
Host: 127.0.0.1:8888\r
If-Modified-Since: Fri, 6 Nov 2020 00:00:00 GMT\r
Cookie: afsd=4654\r
Cache-Control: max-age=0\r
Keep-Alive: timeout=5, max=3\r
Upgrade-Insecure-Requests: 1\r\n\r
Its an HTTP test"""  # 505
    import socket
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((host, port))
    r.send(version_error_msg.encode())
    msg = r.recv(1024).decode()
    r.close()
    return msg


def bad_request(host, port, request_type):
    bad_request_msg = f"""{request_type} /answer.txt HTTP/1.1\r
Connection: keep-alive, keep-alive\r
Host: 127.0.0.1:8888\r
If-Modified-Since: v 2020 13:00:00 GMT\r
Connection: keep-alive\r
Cache-Control: max-age=0\r\a
Keep-Alive: timeout=7, max=5
Upgrade-Insecure-Requests: 1\r\n\r
Its an HTTP test"""  # 400
    import socket
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((host, port))
    r.send(bad_request_msg.encode())
    msg = r.recv(1024).decode()
    r.close()
    return msg


if __name__ == '__main__':
    import sys

    host = "127.0.0.1"
    port = int(sys.argv[1])
    request_type = 'GET'

    version_error(host, port, request_type)
    bad_request(host, port, request_type)
