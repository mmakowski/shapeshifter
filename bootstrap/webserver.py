'''
Invokes other modules to handle incoming HTTP requests. It is a central module that determines
the interface of other modules supported by Shapeshifter.

When a request is received the module to be used is determined based on the first element
of the URI. The module is then loaded and a method corresponding to the HTTP method of the 
request is invoked.

In order to support remote update of the web server itself the process can signal to the running
script that it requires a restart by exiting with code 3.
'''
import cgi
import BaseHTTPServer
import httplib
import imp
import os
import socket
import SocketServer
import sys
import traceback
import urllib
import urlparse

__author__ = 'Maciek Makowski'
__version__ = '1.1.0'


default_port = 5457


class HTTPException(Exception):
    '''
    When raised by a module will cause the error to be reported to the client as a HTTP response.
    '''
    def __init__(self, status, message):
        Exception.__init__(self, message)
        self.status = status

    def send_as_http_response(self, http):
        http.send_error(self.status, self.message)


class _ModuleNotFoundException(Exception):
    def __init__(self, module_name):
        Exception.__init__(self, "module '%s' not found" % module_name)
        self.module_name = module_name


def _load_module(name):
    file_name = '%s.py' % name
    if os.path.isfile(file_name): 
        return imp.load_source(name, file_name)
    else: raise _ModuleNotFoundException(name)


def _mod_name_and_path(path_with_mod):
    try:
        (_, mod, path) = path_with_mod.split('/', 2)
    except ValueError:
        (_, mod) = path_with_mod.split('/', 1)
        path = None
    return (mod, urllib.unquote(path) if path != None else None)


def _allowed_methods(module):
    return sorted(list(set(dir(module)).intersection(set(['DELETE', 'GET', 'POST', 'PUT']))))


class ShapeshifterHTTPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def server_bind(self):
        SocketServer.ThreadingTCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        self.restart_process = False

    def restart(self):
        self.restart_process = True
        self.shutdown()
    

class ShapeshifterHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __parse_form(self):
        self.data = {}
        content_type_header = self.headers.getheader('content-type')
        if content_type_header == None: return
        content_type, pdict = cgi.parse_header(content_type_header)
        if content_type == 'multipart/form-data':
            self.data = cgi.parse_multipart(self.rfile, pdict)
        elif content_type == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            self.data = urlparse.parse_qs(self.rfile.read(length))
        else:
            raise HTTPException(httplib.UNSUPPORTED_MEDIA_TYPE, 
                                'unexpected content type: %s' % content_type)

    def __parse_query_string(self):
        if '?' in self.path: 
            (self.path, query_string) = self.path.split('?', 1)
            self.data.update(urlparse.parse_qs(query_string))

    def __invoke(self, invoke, method):
        try:
            self.__parse_form()
            self.__parse_query_string()
            try:
                (mod_name, path) = _mod_name_and_path(self.path)
            except:
                self.send_error(httplib.BAD_REQUEST, 'Malformed URI: %s. Expected URI format: /<module>[/<path>]')
                return
            try:
                mod = _load_module(mod_name)
            except _ModuleNotFoundException, e:
                self.send_error(httplib.NOT_FOUND, e.message)
                return
            if not method in dir(mod):
                self.send_error(httplib.METHOD_NOT_ALLOWED, 
                                'method not allowed: %s' % method, 
                                {'Allow': ', '.join(_allowed_methods(mod))})
                return
            invoke(mod, path) 
        except HTTPException, e:
            e.send_as_http_response(self)
        except:
            self.send_error(httplib.INTERNAL_SERVER_ERROR, traceback.format_exc())

    def do_DELETE(self):
        def invoke(mod, path): mod.DELETE(self, path)
        self.__invoke(invoke, 'DELETE')

    def do_GET(self):
        def invoke(mod, path): mod.GET(self, path)
        self.__invoke(invoke, 'GET')

    def do_POST(self):
        def invoke(mod, path): mod.POST(self, path)
        self.__invoke(invoke, 'POST')

    def do_PUT(self):
        def invoke(mod, path): mod.PUT(self, path)
        self.__invoke(invoke, 'PUT')

    def send_custom_response(self, content, content_type, status=httplib.OK, headers={}):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        for (key, val) in headers.items(): self.send_header(key, val)
        self.end_headers()
        self.wfile.write(content)

    def send_text_response(self, text, status=httplib.OK, headers={}):
        self.send_custom_response(text, 'text/plain', status, headers)

    def send_error(self, status, message, headers={}):
        self.send_text_response(message, status, headers)

    def send_redirect_response(self, redirect_to):
        self.send_response(httplib.SEE_OTHER)
        self.send_header('Location', redirect_to)
        self.end_headers()


def POST(http, path):
    '''
    Supports the following commands:
    - restart: restarts the web server
    '''
    if path == 'restart': 
        http.send_text_response('the web server will restart shortly', status=httplib.ACCEPTED)
        http.server.restart()
    else:
        raise webserver.HTTPException(httplib.BAD_REQUEST, 'unsupported path: %s' % path)


def _main(port):
    try:
        server = ShapeshifterHTTPServer(('', port), ShapeshifterHandler)
        print 'server starting'
        server.serve_forever()
        print 'server stopped'
        if server.restart_process: sys.exit(3)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        server.socket.close()
        print 'server stopped'


if __name__ == '__main__':
    _main(int(sys.argv[1]) if len(sys.argv) > 1 else default_port)

