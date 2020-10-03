#! /usr/bin/python3
'''
    HTTP server
    Author : Nikhil Adhau
    MIS : 111803035
    Div : I

'''

import sys
from socket import *
import threading

def client_thread (clientSocket, address):
    request_data = clientSocket.recv(1024).decode()
    print (request_data)
    string = "HTTP/1.1 200 OK\n\n<b> Hello There <!b>"
    clientSocket.send(string.encode())
    clientSocket.close()

PORT = int (sys.argv[1]) 
#create a INET(IPV4), (STREAM) TCP socket
try : 
    serverSocket = socket (AF_INET, SOCK_STREAM)
except error as msg:
    print (f"Socket can not be created: {msg}")
    sys.exit(1)
#manipulating options for socket (REUSEADDR lets you use the port whose connection is shutting down)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#bind the socket to localhost and a port
serverSocket.bind(('localhost', PORT))
#start listening
serverSocket.listen(5)
print (f'HTTP server listning on {PORT}')

while True:
    #accept outside connection
    (clientSocket, address) = serverSocket.accept()
    thread = threading.Thread(target = client_thread, args = (clientSocket, address))
    thread.start()
    print (f"New connection request from {address}")

serverSocket.close()
