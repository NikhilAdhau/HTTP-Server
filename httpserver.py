'''
    HTTP server
    Author : Nikhil Adhau
    MIS : 111803035
    Div : I

'''

import sys
from socket import *

PORT = 1300 
#create a INET(IPV4), (STREAM) TCP socket
try : 
    serverSocket = socket (AF_INET, SOCK_STREAM)
except error as msg:
    print (f"Socket can not be created: {msg}")
    sys.exit(1)
#bind the socket to localhost and a port
serverSocket.bind(('localhost', PORT))
#start listening
serverSocket.listen(5)
print (f'HTTP server listning on {PORT}')

while True:
    #accept outside connection
    (clientSocket, address) = serverSocket.accept()
    print (f"New connection request from {address}")
    clientSocket.close()
