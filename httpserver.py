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
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import pytz
import mimetypes
from configparser import ConfigParser, ExtendedInterpolation
import logging
import uuid


class TcpServer ():
    def __init__ (self):
        self.port = parser.getint('settings', 'port')
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
        self.serverSocket.listen(100)
        print (f'HTTP server listening at address \"{self.serverSocket.getsockname()[0]}:{self.serverSocket.getsockname()[1]}\"\n---------------------------------------------------------------------------')

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
        response, fd = self.handle_request(request_data)
        #print (f"response ----- \n {response}")
        clientSocket.sendall(response.encode())
        if fd:
            try :
                clientSocket.sendfile(fd)
                fd.close()
            except:
                 pass
        clientSocket.close()
        
    def handle_request(self, request_data):
        pass
    
class HttpServer(TcpServer):

    headers = {
                "Server" : "Nikhil's Server (Fedora)",
                "Date" : None
              }

    status = {
                200 : 'OK',
                201 : 'Created',
                202 : 'Accepted',
                203 : 'Non-Authoritative Information',
                204 : 'No Content',
                205 : 'Reset Content',
                206 : 'Partial Content',
                300 : 'Multiple Choices',
                301 : 'Moved Permanently',
                302 : 'Found',
                303 : 'See Other',
                304 : 'Not Modified',
                305 : 'Use Proxy',
                307 : 'Temporary Redirect',
                400 : 'Bad Request',
                401 : 'Unauthorized',
                402 : 'Payment Required',
                403 : 'Forbidden',
                404 : 'Not Found',
                405 : 'Method Not Allowed',
                406 : 'Not Acceptable',
                407 : 'Proxy Authentication Required',
                408 : 'Request Timeout',
                409 : 'Conflict',
                410 : 'Gone',
                411 : 'Length Required',
                412 : 'Precondition Failed',
                413 : 'Payload Too Large',
                414 : 'URI Too Long',
                415 : 'Unsupported Media Type',
                416 : 'Range Not Satisfiable',
                417 : 'Expectation Failed',
                426 : 'Upgrade Required',
                501 : 'Not Implemented',
                505 : 'HTTP Version not supported'
             }
    
    #handle all the request and return response
    def handle_request(self, request_data):
        request = HttpRequest(request_data)
        #if request data has any errors
        if request.error or 'host' not in request.headers.keys():
            self.response_code = 400
            response, fd = self.handle_errors(request, self.response_code)
        else:
            #using getattr to handle the particular method returned from the request method
            #getattr because we don't know the name of the method at the time
            try:
                response, fd = getattr(self, f'handle_{request.method}')(request)
            except AttributeError:
                #as HEAD method is similar to GET method
                if request.method == 'HEAD':
                    response, fd = self.handle_GET(request)
                else:
                    self.response_code = 501
                    response, fd = self.handle_errors(request, self.response_code)
        return response, fd

    #handle GET request
    def handle_GET(self, request):
        extra_headers = {}
        filename, redirect_code = self.check_uri(request.uri)
        #if the requested file is not found
        if filename == None:
            self.response_code = 404
            return self.handle_errors(request, self.response_code)
        else:
            file_info = os.stat(filename)
            self.file_size = file_info.st_size
            file_type = mimetypes.guess_type(filename)[0]
            last_modified = format_date_time(file_info.st_mtime)
            if redirect_code:
                if 'if-modified-since' in request.headers.keys() and request.headers['if-modified-since'].lstrip() == last_modified:
                    response_body = ''
                    fd = None
                    self.response_code = 304
                else:
                    response_body = ''
                    fd = None
                    extra_headers.update({ 'Location' : filename})
                    self.response_code = redirect_code
            else:
                if 'if-modified-since' in request.headers.keys() and request.headers['if-modified-since'].lstrip() == last_modified:
                    response_body = ''
                    fd = None
                    self.response_code = 304
                else:
                    response_body, fd = self.response_body(filename)
                    self.response_code = 200
            status_line = self.status_line(self.response_code)
            extra_headers.update({'Content-Length' : self.file_size, 'Last-Modified' : last_modified,  'Content-Type' : file_type})
            response_headers = self.response_headers(request, extra_headers)
            empty_line = "\r\n"
            if request.method == 'HEAD':
                self.handle_logging(request)
                return f"{status_line}{response_headers}{empty_line}{response_body}", None 
            self.handle_logging(request, self.file_size)
            return f"{status_line}{response_headers}{empty_line}{response_body}", fd


    #handle post request
    def handle_POST(self, request):
        status_line = self.status_line(200)
        response_headers = self.response_headers(request, '')
        empty_line = "\r\n"
        print (request.payload)
        return f"{status_line}{response_headers}{empty_line}", None

    #handle delete request
    def handle_DELETE(self, request):
        filename = self.check_uri(request.uri)
        if filename == None:
            return self.handle_errors(404)
        else:
            os.remove(filename)
            status_line = self.status_line(200)
            response_headers = self.response_headers(request, '')
            empty_line = '\r\n'
            response_body = "<b> file has been deleted </b>"
            return f"{status_line}{response_headers}{empty_line}{response_body}", None  
    
    #handle put request
    def handle_PUT(self, request):
        filename = self.check_uri(request.uri)
        if filename == None:
            filename = request.uri.strip('/')
            self.response_code = 201
        else : 
            self.response_code = 204
        filetype = mimetypes.guess_type(filename)[0]
        if filetype == 'text/html':
            with open (filename, 'w') as fd:
                fd.write(request.payload)
        else:
            with open (filename, 'wb') as fd:
                fd.write(request.payload.encode("utf-8"))
        status_line = self.status_line(self.response_code)
        response_headers = self.response_headers(request, '')
        empty_line = "\r\n"
        return f"{status_line}{response_headers}{empty_line}", None

    #handle cookie
    def handle_cookie(self, request):
        try : 
            str = self.address[0] + ',' + request.headers['user-agent']
            with open ('.cookie', 'a+') as f:
                if 'cookie' in request.headers.keys():
                    str1 += str + ',' + request.headers['cookie']
                    print (str)
                    f.seek(0)
                    if  str1 not in f.read():
                        print ('cookie-value not found')
                        f.seek(2)
                        id = uuid.uuid1()
                        f.write(f'{str}, id={id}\n')
                        return f'id={id}'
                    else:
                        return None
                    
                else:
                    print ('cookie not found')
                    id = uuid.uuid1()
                    f.write(f'{str}, id={id}\n')
                    return f'id={id}'
                    
        except :
           return None

    #create a status line
    def status_line(self, status_code):
        status_line = f"HTTP/1.1 {status_code} {self.status[status_code]}\r\n"
        return status_line

    #create response headers
    def response_headers (self, request, extra_headers):
        #get the current date & time
        now = datetime.now()
        stamp = mktime(now.timetuple())
        current_date_time = format_date_time(stamp)
        self.headers['Date'] = current_date_time
        general_headers = ''.join(f"{header}: {self.headers[header]}\r\n" for header in self.headers)
        entity_headers = ''.join(f"{header}: {extra_headers[header]}\r\n" for header in extra_headers)
        cookie = self.handle_cookie(request)
        if cookie:
            entity_headers += 'Set-Cookie:' + cookie + '\r\n'
        response_headers = general_headers + entity_headers
        return response_headers
    
    #handle the URI
    #it returns the file requested as well as it's metadata
    def check_uri (self, filename):
        filename = filename.strip('/')
        if len(filename) == 0:
            filename = "index.html"
        #if the file is present in the directory it will return the filename
        if os.path.isfile(filename):
            return filename, None
        else:
            try:
                with open ('.htaccess', 'r+') as f:
                    lines = f.readlines()
                    for line in lines:
                        if filename in line :
                            field = line.split()
                            filename = field[2]
                            status_code = int(field[0])
                            print (filename, status_code)
                            return filename, status_code
                    return None, None

            except:
                print (" '.htaccess ' file not found")
                return None, None
    
    #handle response_body
    def response_body(self, filename):
        file_type = mimetypes.guess_type(filename)[0]
        if file_type == 'text/html':
            with open(filename, 'r') as f:
                response_body = f.read()
        else:
            f = open (filename, 'rb')
            response_body = ''
        return response_body, f

    #handle error
    def handle_errors(self, request, error_code):
        status_line = self.status_line(error_code)
        response_headers = self.response_headers(request, '')
        error_file = errors_dir + '/' + str(error_code) + '.html'
        with open(error_file) as f:
            response_body = f.read()
        self.handle_logging(request, os.stat(error_file).st_size)
        return f"{status_line}{response_headers}{response_body}\r\n", None

    #logging
    def handle_logging(self, request, file_size = "-"):
        if 'referer' in request.headers.keys():
            ref = request.headers['referer'].lstrip()
        else:
            ref = '-'
        IST =  pytz.timezone('Asia/Kolkata')
        try :
            user_agent = request.headers['user-agent'].lstrip()
        except :
            user_agent = ''
        mesg = f"{self.address[0]} -  - [{datetime.now(IST).strftime('%d/%b/%Y:%H:%M:%S %z')}] \"{request.method} {request.uri} {request.version}\" {self.response_code} {file_size} \"{ref}\" \"user_agent\""
        logger.info(mesg)

class HttpRequest:
    
    def __init__(self, request_data):
        #defining the request attributes
        self.method = None 
        self.uri = None
        self.version = None
        self.headers = {}
        #if request has any error
        self.error  = False

        self.parse_request(request_data)
    
    def parse_request (self, request_data):
        lines = request_data.split('\r\n')
        #parse the request_line
        self.request_line(lines[0])
        #parse the request headers
        index = self.request_headers(lines[1:])
        self.request_body(lines[index + 2:])
        
    def request_line (self, request_line):
        try:
            (self.method, self.uri, self.version) = request_line.split()
        except ValueError:
            self.error = True

    def request_headers (self, lines):
        i = 0
        for index,line in enumerate(lines):
            i = index
            #to check if the line is empty
            if not line.rstrip('\r\n'):
                break
            try:
                (field_name, field_value) = line.split(':', 1)
                self.headers[field_name.lower()] = field_value 
            except ValueError:
                self.error = True
                break
        return i

    def request_body(self, payload): 
        self.payload = '\r\n'.join(line for line in payload)

if __name__ == "__main__":
    #import config file
    parser = ConfigParser(interpolation = ExtendedInterpolation())
    parser.read('myserver.conf')
    #Change the Document directory as per config file
    os.chdir(parser.get('paths', 'DocumentRoot'))
    #errors_file
    errors_dir = parser.get('files', 'errorfiles')
    #logging
    logger = logging.getLogger()
    log_format = '%(message)s'
    logging.basicConfig(filename = parser.get('files', 'logfile'), level = logging.DEBUG, format = log_format)
    server = HttpServer()
    server.serve()
