'''
An utility which issues requests to remote Shapeshifter instances. Can be used in two ways:

1. by importing it in a python script and calling request();
2. by running it from the command line.
'''

import httplib
import mimetypes
import os
import sys
import threading
import traceback

__author__ = 'Maciek Makowski'
__version__ = '1.1.0'


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


def _is_success_status(http_status):
    return http_status < 400


class Result(object):
    '''
    A result of a request to Shapeshifter instance. The field 'success' indicates
    if an invocation was succesful. 
    '''
    def __init__(self, response=None, exception=None):
        self.success = exception == None and response != None and _is_success_status(response.status)
        self.response = response
        self.exception = exception

    def __str__(self):
        return '%s: %s' % ('SUCCESS' if self.success else 'FAILURE',
                           self.__format_response() if self.response != None else self.__format_exception())

    def __format_response(self):
        resp_str = self.response.read()
        if len(resp_str) == 0:
            fmt_resp = ''
        elif not '\n' in resp_str:
            fmt_resp = ': %s' % resp_str
        else:
            fmt_resp = ':\n%s' % resp_str
        return '%s, %s%s' % (self.response.status, self.response.reason, fmt_resp)

    def __format_exception(self):
        return self.exception


class _Requester(threading.Thread):
    def __init__(self, target, method, uri, form_data, content_type):
        threading.Thread.__init__(self)
        self.target = target
        self.method = method
        self.uri = uri
        self.form_data = form_data
        self.content_type = content_type
        self.result = None

    def run(self):
        try:
            conn = httplib.HTTPConnection(self.target)
            conn.request(self.method, self.uri, self.form_data, {'Content-type': self.content_type})
            self.result = Result(response = conn.getresponse())
        except Exception, e:
            self.result = Result(exception = traceback.format_exc(e))


def request(targets, uri, method='POST', properties={}, files={}):
    '''
    Sends a request to Shapeshifter web servers. 
    - targets: a list of web server URLs, each in format "host:port" or "host", in which case the default
               port will be assumed
    - uri: the URI to request from each server
    - method: the HTTP method to use
    - properties: text fields to be submitted in the request
    - files: files to be sent in the request; each entry should map a form id to a local file path, the file
             will be read and its contents sent.
    Returns a dictionary mapping server names (as specified in targets list) to Result objects.
    '''
    targets = [t if ':' in t else '%s:%s' % (t, default_port) for t in targets]
    file_data = [(id, os.path.basename(path), _file_content(path)) for (id, path) in files.items()]
    content_type, form_data = _encode_multipart_formdata(properties.items(), file_data)
    requesters = []
    for target in targets:
        requester = _Requester(target, method, uri, form_data, content_type)
        requesters.append(requester)
        requester.start()
    results = dict()
    for requester in requesters: 
        requester.join()
        results[requester.target] = requester.result
    return results
    

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


def _main():
    if len(sys.argv) < 4:
        _print_usage()
        sys.exit(2)
    targets = sys.argv[1].split(',')
    method = sys.argv[2]
    uri = sys.argv[3]
    (properties, files) = _split_form_data(sys.argv[4]) if len(sys.argv) > 4 else ({}, {})
    results = request(targets, uri, method, properties, files)
    for (target, result) in results.items():
        print '-- invocation result for %s --' % target
        print result
        print '----'


if __name__ == '__main__':
    _main()

