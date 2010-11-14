'''
Provides functions for handling uploads and downloads of files.
'''
import cgi
import httplib
import os
import webserver

__author__ = 'Maciek Makowski'
__version__ = '0.2.0'


def GET(http, path):
    '''
    Sends back contents of the file. The Content-type of the response is set to the value of Content-type 
    query parameter.
    '''
    if not os.path.isfile(path):
        raise webserver.HTTPException(httplib.NOT_FOUND, 'file not found: %s' % path)
    with open(path) as f: content = f.read()
    content_type = http.data['Content-type'][0] if http.data.has_key('Content-type') else 'application/octet-stream'
    http.send_custom_response(content, content_type)


def PUT(http, path):
    '''
    Creates a file sent in a form. Expects a single entry with key 'file'; the value should be the file contents.
    '''
    contents = http.form_data.get('file')
    dirname = os.path.dirname(path)
    if len(dirname) > 0 and not os.path.isdir(dirname): os.makedirs(dirname)
    with open(path, 'wb') as f:
        for content_part in contents:
            f.write(content_part)
    http.send_response(httplib.CREATED)
    http.end_headers()
