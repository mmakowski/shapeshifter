'''
Invokes other modules to handle incoming HTTP requests.
'''
import httplib
import imp
import os
import sys
import traceback
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

__author__ = 'Maciek Makowski'
__version__ = '0.0.1'

port = 5457


class ModuleNotFoundException(Exception):
    def __init__(self, module_name):
        Exception.__init__(self, "module '%s' not found" % module_name)
        self.module_name = module_name


def load_module(name):
    file_name = '%s.py' % name
    if os.path.isfile(file_name): 
        return imp.load_source(name, file_name)
    else: raise ModuleNotFoundException(name)


def mod_name_and_path(path_with_mod):
    try:
        (_, mod, path) = path_with_mod.split('/', 2)
    except ValueError:
        (_, mod) = path_with_mod.split('/', 1)
        path = None
    return (mod, path)

    
class ShapeshifterHandler(BaseHTTPRequestHandler):
    def __invoke(self, invoke):
        try:
            try:
                (mod_name, path) = mod_name_and_path(self.path)
            except:
                self.send_error(httplib.BAD_REQUEST, 'Malformed URI: %s. Expected URI format: /<module>[/<path>]')
            try:
                mod = load_module(mod_name)
            except ModuleNotFoundException, e:
                self.send_error(httplib.NOT_FOUND, e.message)
                return
            invoke(mod, path)
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


def main():
    try:
        server = HTTPServer(('', port), ShapeshifterHandler)
        print 'server starting'
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
        print 'server stopped'


if __name__ == '__main__':
    main()

