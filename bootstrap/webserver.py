'''
Invokes other modules to handle incoming HTTP requests.
'''
import BaseHTTPServer
import httplib
import imp
import os
import socket
import SocketServer
import sys
import traceback

# Shapeshifter modules
import html

__author__ = 'Maciek Makowski'
__version__ = '0.0.1'

port = 5457


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
    return (mod, path)


class _ShapeshifterHTTPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def server_bind(self):
        SocketServer.ThreadingTCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

    def restart(self):
        self.shutdown()
        self.restart_process = True
    

class _ShapeshifterHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __invoke(self, invoke):
        try:
            try:
                (mod_name, path) = _mod_name_and_path(self.path)
            except:
                self.send_error(httplib.BAD_REQUEST, 'Malformed URI: %s. Expected URI format: /<module>[/<path>]')
            try:
                mod = _load_module(mod_name)
            except _ModuleNotFoundException, e:
                self.send_error(httplib.NOT_FOUND, e.message)
                return
            invoke(mod, path) 
        except HTTPException, e:
            e.send_as_http_response(self)
        except:
            self.send_error(httplib.INTERNAL_SERVER_ERROR, traceback.format_exc())

    def do_DELETE(self):
        def invoke(mod, path): mod.DELETE(self, path)
        self.__invoke(invoke)

    def do_GET(self):
        def invoke(mod, path): mod.GET(self, path)
        self.__invoke(invoke)

    def do_POST(self):
        def invoke(mod, path): mod.POST(self, path)
        self.__invoke(invoke)

    def do_PUT(self):
        def invoke(mod, path): mod.PUT(self, path)
        self.__invoke(invoke)


def POST(http, path):
    '''
    Supports the following commands:
    - restart: restarts the web server
    '''
    if path == 'restart': 
        html.send_html_response(http, 
                                title='web server restart', 
                                body='the web server will restart shortly', 
                                status=httplib.ACCEPTED)
        http.server.restart()


def main():
    try:
        server = _ShapeshifterHTTPServer(('', port), _ShapeshifterHandler)
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
    main()

