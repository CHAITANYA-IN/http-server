# http-server
Simple Http server that generates logs and allows client-server communication via browser as well as using command line.

To run the server 
`python3 server.py`
Port number is selected randomly everyime the server starts

To test (using testing.py)
`python3 testing.py <port-number>`
<port number> : Port number of the server

Files in the project:

To configure the server, to know about the access and error log location 
Access the file ***amchat.conf***

To see all the requests
Access the file ***access.log***

To see only the errors 
Acccess the file ***error.log***

To view the active cookies( not expired )
Access the file ***cookies.log***

Response Generator file
***requirement.py***

Module file imported in ***testing.py***
***client.py***

Our default file is success.html (index.html of apache2)
If a page successfully loads, it gets redirected to success.html
If a file is not found, error.html is used.
Before testing, do create a file ***otps.txt*** and change its permission to read-only.

Use these for generating ***otps.txt***
`touch otps.txt`
`sudo chmod -rwx otps.txt`
