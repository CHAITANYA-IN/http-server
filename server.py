from threading import *
from requirement import *
from socket import *
import random
import datetime

HOST = "127.0.0.1"
PORT = random.randint(12000, 14999)
CLIENTS = []
THREADS = []


def service(conn, address, number):
    request = conn.recv(1024).decode()
    if(request != ""):
        response, _, _ = response_to_request(request)
        conn.send(response)
        print('Response sent Successfully')
    conn.close()


s = socket(AF_INET, SOCK_STREAM)        # Creating a socket
s.bind((HOST, PORT))                  # Binding that socket
s.listen(5)                            # listening on that socket
print("Listening at ", s.getsockname())  # Printing the socket
count = 0

while True:
    try:
        conn, addr = s.accept()
        print(conn, addr)
        service(conn, addr, 0)
    except KeyboardInterrupt:
        break
s.close()