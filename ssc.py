'''
An utility which issues requests to remote Shapeshifter instances. Can be used in two ways:

1. by importing it in a python script and calling request();
2. by running it from the command line.
'''

import httplib
import mimetypes
import os
import sys

default_port = 5457

def _encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance

    Taken from http://code.activestate.com/recipes/146306/
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % _get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def _file_content(path):
    with open(path, 'rb') as f: return f.read()


def request(targets, uri, method='POST', properties={}, files={}):
    '''
    Sends a request to Shapeshifter web servers. 
    - targets: a list of web server URLs, each in format "host:port"
    - uri: the URI to request from each server
    - method: the HTTP method to use
    - properties: text fields to be submitted in the request
    - files: files to be sent in the request; each entry should map a form id to a local file path, the file
             will be read and its contents sent.
    '''
    file_data = [(id, os.path.basename(path), _file_content(path)) for (id, path) in files.items()]
    content_type, form_data = _encode_multipart_formdata(properties.items(), file_data)
    responses = dict()
    for target in targets:
        conn = httplib.HTTPConnection(target)
        conn.request(method, uri, form_data, {'Content-type': content_type})
        responses[target] = conn.getresponse()
    return responses
    

def _print_usage():
    print 'ssc targets method URI [mappings]'


def _split_form_data(data_map):
    properties = dict()
    files = dict()
    for (key, value) in [tuple(m.split('=')) for m in data_map.split(',')]:
        if value.startswith('file:'):
            files[key] = value[5:]
        else:
            properties[key] = value
    return (properties, files)


def main():
    if len(sys.argv) < 4:
        _print_usage()
        sys.exit(2)
    targets = [t if ':' in t else '%s:%s' % (t, default_port) for t in sys.argv[1].split(',')]
    method = sys.argv[2]
    uri = sys.argv[3]
    (properties, files) = _split_form_data(sys.argv[4]) if len(sys.argv) > 4 else ({}, {})
    responses = request(targets, uri, method, properties, files)
    for (target, response) in responses.items():
        print '-- response from %s --' % target
        print response.status, response.reason
        print response.read()
        print '----'


if __name__ == '__main__':
    main()

