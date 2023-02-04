#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, https://github.com/StevenJiao
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return f'Code: {self.code}\nBody: {self.body}'

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        lines = data.split('\r\n')
        return int(lines[0].split(' ')[1])

    def get_headers(self,data):
        lines = data.split('\r\n\r\n')
        return lines[0]

    def get_body(self, data):
        lines = data.split('\r\n\r\n')
        return lines[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def append_args(self, url: str, args: dict) -> str:
        # append a ? to signify arguments if there isn't already any
        url = (url + '?') if ('?' not in url) else url

        # iterate through the keys and add the arguments 
        for i, arg in enumerate(args.keys()):
            url += arg + "=" + args[arg]

            # Add an & if we're not at the last arg yet
            if i < len(args) - 1:
                url += '&'
        
        return url

    def convert_query_to_args(self, args: dict, query: str):
        args = {} if not args else args

        query_split = query.split("&")
        for key_val in query_split:
            key_val_split = key_val.split('=')
            args[key_val_split[0]] = key_val_split[1]
        return args
        

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # parse the URL
        parsedUrl = urllib.parse.urlparse(url)

        # connect to the server
        self.connect(parsedUrl.hostname, parsedUrl.port if parsedUrl.port else 80)

        # check that path has something and also add the query if the url came with any
        new_url_path = '/' if not parsedUrl.path else parsedUrl.path
        new_url_path = new_url_path + '?' + parsedUrl.query if parsedUrl.query else new_url_path

        # add arguments if there are any
        new_url_path = self.append_args(new_url_path, args) if args else new_url_path

        # send our GET request
        req = f"GET {new_url_path} HTTP/1.1\r\n" \
                f"Host: {parsedUrl.hostname}\r\n\r\n"
        self.sendall(req)

        # wait for a response
        resp = self.recvall(self.socket)

        # get the code and body
        code = self.get_code(resp)
        body = self.get_body(resp)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # parse the URL
        parsedUrl = urllib.parse.urlparse(url)

        # connect to the server
        self.connect(parsedUrl.hostname, parsedUrl.port if parsedUrl.port else 80)

        # check if we have anything in the url path
        new_url_path = '/' if not parsedUrl.path else parsedUrl.path

        # add the original URL arguments to our args if there was any
        args = self.convert_query_to_args(args, parsedUrl.query) if parsedUrl.query else args

        # URL encode our args
        data = urllib.parse.urlencode(args) if args else None

        # send our full POST request with body of urlencoded args
        req = f"POST {new_url_path} HTTP/1.1\r\n" \
                f"Host: {parsedUrl.hostname}\r\n" \
                "Content-Type: application/x-www-form-urlencoded\r\n" \
                f"Content-Length: {len(data) if data else 0}\r\n" \
                f"\r\n{data}"
        self.sendall(req)

        # wait for a response
        resp = self.recvall(self.socket)

        # get the code and body
        code = self.get_code(resp)
        body = self.get_body(resp)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
