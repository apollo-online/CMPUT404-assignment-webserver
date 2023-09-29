#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright Â© 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data =  self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data.decode())
        if (self.data.decode() == ''): # block random empty requests that crash list index
            return
        
        headers = self.data.decode().split('\n') # parse HTTP headers
        http_request = headers[0].split()[0]
        filename = headers[0].split()[1]

        if (http_request != 'GET'): # guard against illegal requests
            response = 'HTTP/1.0 405 Method Not Allowed\n\n'
            self.request.sendall(response.encode())
            return 

        if filename == '/': # deal with root request
            filename = '/index.html'
      
        if (".." in filename): # directory traversal attack prevention; adapted from: https://stackoverflow.com/a/6803714
            current_directory = os.path.abspath(os.curdir) 
            requested_path = os.path.relpath('./www' + filename, start=current_directory)
            requested_path_abs = os.path.abspath(requested_path)
            common_prefix = os.path.commonprefix([requested_path_abs, current_directory + '/www'])
            if (common_prefix != current_directory + '/www'):
                response = 'HTTP/1.0 404 Bad Request\n\n'
                self.request.sendall(response.encode())
                return 
                          
        if (os.path.isdir('./www' + filename)): # directory request
            if (filename[-1] != "/"): # redirect if missing '/'
                new_location = 'Location: ' + filename + '/'
                response = 'HTTP/1.0 301 Permanently Moved' + '\n' + new_location 
                self.request.sendall(response.encode())
                return 

            fin = open('./www' + filename + '/index.html') # open index.html if directory request
            content = fin.read()
            fin.close()

            content_type = "Content-Type: text/html; charset=utf-8" # html header because we need to show index.html for directory request
            response = 'HTTP/1.0 200 OK' + '\n' + content_type + '\n' + '\n' + content 
            self.request.sendall(response.encode())
            return

        try: # if not directory request, file request; attempt to open file
            fin = open('./www' + filename)
            content = fin.read()
            fin.close()

        except FileNotFoundError: # file does not exist
            response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found' 
            self.request.sendall(response.encode())
            return
        
        if (".css" in filename): # attach appropiate header for css
            content_type = "Content-Type: text/css; charset=utf-8"
            response = 'HTTP/1.0 200 OK' + '\n' + content_type + '\n' + '\n' + content
            self.request.sendall(response.encode())
            return

        if (".html" in filename): # attach appropiate header for html
            content_type = "Content-Type: text/html; charset=utf-8"
            response = 'HTTP/1.0 200 OK' + '\n' + content_type + '\n' + '\n' + content
            self.request.sendall(response.encode())
            return

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()