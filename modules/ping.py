'''
Responds to ping.
'''
import httplib
import webserver

__author__ = 'Maciek Makowski'
__version__ = '1.0.0'


def POST(http, path):
    if path == None or len(path) == 0: http.send_text_response('pong')
    else: raise webserver.HTTPException(httplib.BAD_REQUEST, 'unsupported path: %s' % path)
