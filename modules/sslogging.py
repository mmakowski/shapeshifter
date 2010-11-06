'''
Provides functions for thread-safe logging and for including logs in HTTP responses.
'''
import httplib
import logging
import StringIO
import threading

__author__ = 'Maciek Makowski'
__version__ = '1.0.0'

_thread_local = threading.local()

def send_log_response(http, status=httplib.OK):
    '''
    Sends current log as a HTTP response and closes the logger.
    '''
    _stop_logging()
    http.send_response(status)
    http.send_header('Content-type', 'text/plain')
    http.end_headers()
    http.wfile.write(_thread_local.buffer.getvalue())
    _thread_local.buffer.close()

def start_logging():
    '''
    Initialises logging. Messages logged after this call will be sent when send_log_response() is called.
    '''
    _thread_local.buffer = StringIO.StringIO()
    handler = logging.StreamHandler(_thread_local.buffer)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(logging.DEBUG)
    _thread_local.logger = logging.getLogger(threading.current_thread().name)
    _thread_local.logger.setLevel(logging.DEBUG)
    _thread_local.logger.addHandler(handler)

def debug(msg):
    _thread_local.logger.debug(msg)

def info(msg):
    _thread_local.logger.info(msg)

def warn(msg):
    _thread_local.logger.warn(msg)

def error(msg):
    _thread_local.logger.error(msg)

def critical(msg):
    _thread_local.logger.critical(msg)

def _stop_logging():
    for handler in _thread_local.logger.handlers: 
        handler.flush()
        _thread_local.logger.removeHandler(handler)
