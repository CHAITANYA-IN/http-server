import time
import requests
import sys
import client

HOST = '127.0.0.1'
PORT = int(sys.argv[1])


# Simple GET
# Homepage Access
r = requests.get(f"http://{HOST}:{PORT}")

# Response 200
print("1.Checking for GET REQUEST 200 status...")
r = requests.get(f"http://{HOST}:{PORT}/answer.txt")
if(r.status_code == 200):
    print("1.Success")
else:
    print("1.Fail")
# Response 304
print("2.Checking for GET REQUEST 304 status...")
r = client.not_modified(HOST, PORT, 'GET')  
if(int(r.split(" ")[1]) == 304):
    print("2.Success")
else:
    print("2.Fail")
# Response 404
print("5.Checking for GET REQUEST 404 status...")
r = requests.get(f"http://{HOST}:{PORT}/httpd.txt") 
if(r.status_code == 404):
    print("5.Success")
else:
    print("5.Fail")
# Response 505
print("3.Checking for GET REQUEST 505 status...")  
r = client.version_error(HOST, PORT, 'GET')
if(int(r.split(" ")[1]) == 505):
    print("3.Success")
else:
    print("3.Fail")
# Response 400
print("4.Checking for GET REQUEST 400 status...")
r = client.bad_request(HOST, PORT, 'GET')  
if(int(r.split(" ")[1]) == 400):
    print("4.Success")
else:
    print("4.Fail")

# Response 403
print("6.Checking for GET REQUEST 403 status...")
r = requests.get(f"http://{HOST}:{PORT}/otps.txt") 
if(r.status_code == 403):
    print("6.Success")
else:
    print("6.Fail")


# Simple Post

print("7.Checking for POST REQUEST ...")
r = requests.post(f"http://{HOST}:{PORT}/form1.html",
                  params={'fname': 'amey', 'lname': 'dhongade'})  
if(r.status_code == 200):
    print("7.Success")
else:
    print("7.Fail")


# Simple Put
data = """
<html>
<head>
<title>
Response to PUT Request
</title>
</head>
</html>
"""

print("8.1.Checking for PUT REQUEST ...")
r = requests.put(f"http://{HOST}:{PORT}/dummy.html",
                 data=data)  
if(r.status_code == 204):
    print("8.1.Success")
else:
    print("8.1.Fail")
print("8.2.Checking for PUT REQUEST Non-existing file...")
r = requests.put(f"http://{HOST}:{PORT}/uploaded.html",
                 data=data)  
if(r.status_code == 201):
    print("8.2.Success")
else:
    print("8.2.Fail")


# Simple Delete


print("9.Checking for DELETE REQUEST ...")
r = requests.delete(f"http://{HOST}:{PORT}/dummy.html")  
if(r.status_code == 200):
    print("9.Success")
else:
    print("9.Fail")
# Deleting a file that does not exist
print("10.Checking for DELETE REQUEST Non-existing file...")
r = requests.delete(f"http://{HOST}:{PORT}/anwser.html") 
if(r.status_code == 204):
    print("10.Success")
else:
    print("10.Fail")


# Simple Head


print("11.Checking for HEAD REQUEST ...")
r = requests.head(f"http://{HOST}:{PORT}/success.html")  
if(r.status_code == 200):
    print("11.Success")
else:
    print("11.Fail")

# response 304
print("12.Checking for HEAD REQUEST 304 status...")
r = client.not_modified(HOST, PORT, 'HEAD')  
if(int(r.split(" ")[1]) == 304):
    print("12.Success")
else:
    print("12.Fail")
# Response 505 int(r.spilt())==505
print("13.Checking for HEAD REQUEST 505 status...")
r = client.version_error(HOST, PORT, 'HEAD')  # http VERSION Mismatch
if(int(r.split(" ")[1]) == 505):
    print("13.Success")
else:
    print("13.Fail")
# Response 400
print("14.Checking for HEAD REQUEST 400 status...")
r = client.bad_request(HOST, PORT, 'HEAD')  
if(int(r.split(" ")[1]) == 400):
    print("14.Success")
else:
    print("14.Fail")
# Response 404
print("15.Checking for HEAD REQUEST 404 status...")
r = requests.head(f"http://{HOST}:{PORT}/httpd.txt")  
if(r.status_code == 404):
    print("15.Success")
else:
    print("15.Fail")
r = requests.head(f"http://{HOST}:{PORT}/answer.txt")
# Response 403
print("16.Checking for HEAD REQUEST 403 status...")
r = requests.head(f"http://{HOST}:{PORT}/otps.txt") 
if(r.status_code == 403):
    print("16.Success")
else:
    print("16.Fail")
