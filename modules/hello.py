'''
A simple demo module.
'''

# Shapeshifter modules:
import html


__author__ = 'Maciek Makowski'
__version__ = '1.0.0'


def POST(http, path):
    '''
    Say hello.
    '''
    print('Hello %s!' % path)
    http.send_response(200)

