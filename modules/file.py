'''
Provides functions for handling uploads of files.
'''
import cgi
import httplib
import os

# Shapeshifter modules:
import form


__author__ = 'Maciek Makowski'
__version__ = '0.0.1'


def PUT(http, path):
    '''
    Creates a file sent in a form. Expects a single entry with key 'file'; the value should be the file contents.
    '''
    data = form.parse_form(http)
    contents = data.get('file')
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    with open(path, 'wb') as f:
        for content_part in contents:
            f.write(content_part)
    http.send_response(httplib.CREATED)
    http.end_headers()
