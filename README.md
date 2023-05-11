# HTTP Server
Simple Http server that generates logs and allows client-server communication via browser as well as using command line.

### How to run
To run the server 
```sh
python3 server.py
```
Port number is selected randomly everytime the server starts

To test (using testing.py)
```sh
python3 testing.py <port-number>
```
<port number> : Port number of the server

### Important Files:

***amchat.conf***

To configure the server, to know about the access and error log location 

***access.log***

To see all the requests

***error.log***

To see only the errors

***cookies.log***

To view the active cookies (not expired)

***requirement.py***

Response Generator file

***client.py***

Creates client

***testing.py***

Tests HTTP server by spawning clients

***success.html***, ***error.html***

Equivalent to index.html
If a page successfully loads, it gets redirected to success.html
If a file is not found, error.html is used.
  
***otps.txt***

Before testing, do create this file and change its permission to read-only.
```sh
touch otps.txt
sudo chmod -rwx otps.txt
```
