'''
An utility which issues requests to remote Shapeshifter instances.
'''

import httplib
import mimetypes
import os

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


def _print_usage():
    print 'ssc targets URI method [mappings]'


def _file_content(path):
    with open(path) as f: return f.read()


def request(targets, uri, method='POST', properties={}, files={}):
    file_data = [(id, os.path.basename(path), _file_content(path)) for (id, path) in files.items()]
    content_type, form_data = _encode_multipart_formdata(properties.items(), file_data)
    responses = dict()
    for target in targets:
        conn = httplib.HTTPConnection(target)
        conn.request(method, uri, form_data, {'Content-type': content_type})
        responses[target] = conn.getresponse()
    return responses
    

def main():
    responses = request(['localhost:%s' % default_port], '/ssmodule/ssc', method='PUT', files={'module': 'ssc.py'})
    resp = responses.values()[0]
    print resp.status, resp.reason
    print resp.read()


if __name__ == '__main__':
    main()

