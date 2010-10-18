'''
Provides functions for dealing with HTTP forms.
'''
import cgi
import httplib

# Shapeshifter modules:
import webserver


__author__ = 'Maciek Makowski'
__version__ = '0.0.1'


def parse_form(http):
    '''
    Parses data encoded as multipart/form-data.
    '''
    content_type, pdict = cgi.parse_header(http.headers.getheader('content-type'))
    if content_type != 'multipart/form-data':
        raise webserver.HTTPException(httplib.UNSUPPORTED_MEDIA_TYPE, 
                                      'expected content type: multipart/form-data, was: %s' % content_type)
    return cgi.parse_multipart(http.rfile, pdict)

