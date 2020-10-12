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
import os

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
                (clientSocket, self.address) = self.serverSocket.accept()
            except KeyboardInterrupt:
                print ("\nShutting down the server.....")
                sys.exit()
            print (f"New connection request from {self.address}")
            thread = threading.Thread(target = self.client_thread, args = [clientSocket])
            thread.start()
            
        self.serverSocket.close()

    def client_thread (self, clientSocket):
        #while True:
        request_data = clientSocket.recv(1024).decode()
        print (request_data)   
        response = self.handle_request(request_data)
        clientSocket.send(response.encode())
        clientSocket.close()
    
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
                404 : 'Not Found',
                501 : 'Not Implemented',
                505 : 'HTTP Version not supported'
             }
    
    #handle all the request and return response
    def handle_request(self, request_data):
        request = HttpRequest(request_data)
        #using getattr to handle the particular method returned from the request method
        #getattr because we don't know the name of the method at the time
        try:
            response = getattr(self, f'handle_{request.method}')(request)
        except AttributeError:
            response = self.handle_501_error()
        return response

    def handle_501_error(self):
        status_line = self.status_line(501)
        response_headers = self.response_headers()
        return f"{status_line}{response_headers}\r\n"

    #handle 400 error
    def handle_400_error(self, request):
        status_line = self.status_line(400)
        response_headers = self.response_headers()
        return f"{status_line}{response_headers}\r\n"

    #handle get request
    def handle_GET(self, request):
        #host field is required in HTTP/1.1
        #if 'HOST' in request.headers:
        #    status_line = self.status_line(200)
        #else:
        #    status_line = self.status_line(400)

        #handle the uri
        file = request.uri.strip('/')
        
        if os.path.exists(file):
            status_line = self.status_line(200)
            with open(file) as f:
                response_body = f.read()
        else:
            status_line = self.status_line(404)
            response_body = "<b> File Not Found! <!b>"
        response_headers = self.response_headers()
        empty_line = "\r\n"
        return f"{status_line}{response_headers}{empty_line}{response_body}"

    #handle post request
    def handle_POST(self, request):
        status_line = self.status_line(200)
        response_headers = self.response_headers()
        empty_line = "\r\n"
        return f"{status_line}{response_headers}{empty_line}"

    #create a status line
    def status_line(self, status_code):
        status_line = f"HTTP/1.1 {status_code} {self.status[status_code]}\r\n"
        return status_line

    #create response headers
    def response_headers (self):
        response_headers = ''.join(f"{header}: {self.headers[header]}\r\n" for header in self.headers)
        return response_headers

class HttpRequest:
    def __init__(self, request_data):
        #defining the request attributes
        self.method = None 
        self.uri = None
        self.version = None
        self.headers = {}

        self.parse_request(request_data)
    
    def parse_request (self, request_data):
        lines = request_data.split('\r\n')
        #parse the request_line
        self.request_line(lines[0])
        #parse the request headers
        self.request_headers(lines[1:])
        
    def request_line (self, request_line):
        try:
            (self.method, self.uri, self.version) = request_line.split()
        except ValueError:
            self.method = '400_error'

    def request_headers (self, lines):
        for line in lines:
            if not line.rstrip('\r\n'):
                break
            (field_name, field_value) = line.split(':', 1)
            self.headers[field_name] = field_value 

if __name__ == "__main__":
    server = HttpServer()
    server.serve()
