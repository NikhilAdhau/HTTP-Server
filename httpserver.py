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

class httpServer ():
    def __init__ (self, port = 1300):
        self.port = port
        #create a INET(IPV4), (STREAM) TCP socket
        try : 
            self.serverSocket = socket (AF_INET, SOCK_STREAM)
        except error as msg:
            print (f"Socket can not be created: {msg}")
            sys.exit(1)
        #manipulating options for socket (REUSEADDR lets you use the port whose connection is shutting down)
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #bind the socket to localhost and a port
        try:
            self.serverSocket.bind(('localhost', self.port))
        except error as msg:
            print (f"Socket can not be bound to {self.port} : {msg}")
            sys.exit(1)
        #start listening
        self.serverSocket.listen(5)
        print (f'HTTP server listning on {self.port}')
    

    def client_thread (self):
        #while True:
        self.request_data = self.clientSocket.recv(5000).decode()
        if not self.request_data.strip():
            clientSocket.close()
        print (self.request_data)   
        self.interpret()
        string = "HTTP/1.1 200 OK\n\n<b> Hello There <!b>"
        self.clientSocket.send(string.encode())
        self.clientSocket.close()
    
    def interpret (self):
        #extracting the request line
        request_line = self.request_data.splitlines()[0].rstrip('\r\n')
        (self.request_method, self.url_path, self.http_version) = request_line.split()
        if self.request_method == "GET":
            pass
        else:
            print ("hey")
    
    def serve (self):
        while True:
            #accept outside connection
            try:
                (self.clientSocket, self.address) = self.serverSocket.accept()
            except KeyboardInterrupt:
                print ("\nShutting down the server.....")
                sys.exit()
            print (f"New connection request from {self.address}")
            thread = threading.Thread(target = self.client_thread)
            thread.start()
            
        self.serverSocket.close()


if __name__ == "__main__":
    try:
        port = int (sys.argv[1])
        server = httpServer(port)
    except ValueError:
        print (f"usage : sys.argv[0] [port-number]")
        sys.exit(1)
    except:
        server = httpServer()
    server.serve()
