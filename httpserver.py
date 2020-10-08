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

class TcpServer ():
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
        print (f'HTTP server listining at - {self.serverSocket.getsockname()}')

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

    def client_thread (self):
        #while True:
        request_data = self.clientSocket.recv(1024).decode()
        print (request_data)   
        self.handle_request(request_data)
        self.clientSocket.close()
    
    def handle_request(self, request_data):
        pass
    
class HttpServer(TcpServer):
    headers = {
                "Server" : "Nikhil's Server (Pop-os)",
                "Date" : "Thu, 08 Oct 2020 12:40:27 GMT",
                "Last-Modified" : "Thu, 08 Oct 2020 12:40:27 GMT"
              }

    status = {
                200 : 'OK',
                400 : 'Bad Request',
                505 : 'HTTP Version not supported'
             }
    
    def handle_request(self, request_data):
        request = HttpRequest(request_data)

class HttpRequest:
    def __init__(self, request_data):
        #defining the request attributes
        self.method = None
        self.uri = None
        self.version = None
        self.headers = {}

        self.parse_request(request_data)
    
    def parse_request (self, request_data):
        lines = request_data.splitlines('\r\n')
        print (line for line in lines)
        

if __name__ == "__main__":
    server = TcpServer()
    server.serve()
