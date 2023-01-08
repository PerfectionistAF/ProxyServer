from socket import *
import socket
import sys
import requests
import http.server
import socketserver

from setuptools import config

if len(sys.argv) <= 1:
    server_name = socket.gethostname()
    server_port = 5001
    print('Usage : "python ProxyServer.py server_ip"\nserver_name : It is the name Of Proxy Server:', server_name)
    server_address = socket.gethostbyname(server_name)
    server_ip = '127.0.0.1'
    print('server_ip : It is the IP Address Of Proxy Server:', server_ip)
    #sys.exit(2)
# Create a remote server socket, bind it to a port and start listening
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcpSerSock.bind(('', server_port))
    tcpSerSock.listen(5)
    print("Server started successfully")
except Exception as e:
    print(e)
    sys.exit(0)

while 1:
# Start recieving data from the client, STEP: PROXY RECEIVES USER'S REQUEST
    print('\n\nReady to serve...')
    tcpCliSock, user_addr = tcpSerSock.accept()    #Waits for incoming connection
    request = tcpCliSock.recv(8192)                #Proxy Server receives request
    message = tcpCliSock.recv(8192).decode()  # Decode the received data from client socket (TCP connection)
    print('Received a connection from:', user_addr)
    print(message)
#Check if file name is present among the cached files, STEP: CACHE HIT/ FILE CACHING
    start = request.split('\n')[0]
    source_url = start.split()[1]
    print('URL: ', source_url)
#URL FILTER
    with open(r'URLFILTERDB.txt', 'r') as file:
        content = file.readlines()
        if source_url in content:
            print('URL is blocked')
        else:
            print('Continue to cache check')

    filename = request.split()[1].partition("/")[2]
    print('Actual file name requested from remote server:', filename)
    fileExist = "false"
    filetouse = "/" + filename
    print(filetouse)
    try:
        # Check whether the file exist in the cache: IN CASE FOUND
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()  #each line in file as a list item
        fileExist = "true"
        print("Requested file found in cache:", filetouse)
        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.0 200 OK\r\n")              #Send from client socket to ps
        tcpCliSock.send("Content-Type:text/html\r\n")
        #When lines of file actually exist: go over them and print
        for i in range(0 , len(outputdata)):
            print('Found in cache:', tcpCliSock.send(outputdata[i]))

# Error handling for file not actually found in cache, STEP: FORWARD THE REQUEST TO REMOTE SERVER
    except IOError:
        if fileExist == "false":
            print("Requested file NOT found in cache, perform GET to server for file:", filetouse)
            # Create a socket on the proxyserver
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            http_pos = source_url.find("://")
            #Skip www if possible
            held = source_url[http_pos:]
            webserver_name = held.replace("www.", "", 1)
            print('Web server we send the un-cached request to', webserver_name)
            hostn = filename.replace("www.", "", 1)
            try:
                # Connect web server to the socket to port 80
                c.connect('webserver_name', 80)
                # Create a temporary file, executable/nonsource on this socket and ask port 80 for the file requested by client
                fileobj = c.makefile('r', 0)
                fileobj.write("GET " + "http://" + filename + " HTTP/1.0\n\n")
                # Read the response into buffer, STEP: TIME TO CACHE FOR NEXT REQUEST
                buffer = fileobj.readlines()
                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                tmpFile = open("./" + filename, "wb")
                for i in range(0 , len(buffer)):
                    tcpCliSock.send(buffer[i])
                    tmpFile.write(buffer[i])
                    #c.sendall(buffer[i])
            except:
                print("Illegal request")
        else:
            # HTTP response message for file not found, STEP: ALLOW PROXY SERVER TO RETURN ERROR 404
            tcpCliSock.send("HTTP/ 1.1 404 Not Found\r\n")
            tcpCliSock.send("Content-Type:text/html\r\n")
            tcpCliSock.send("\r\n")
    # Close the client and the server sockets
    tcpCliSock.close()
tcpSerSock.close()
