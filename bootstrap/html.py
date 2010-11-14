'''
Provides functions and templates for generating HTML reponses.
'''
import httplib

__author__ = 'Maciek Makowski'
__version__ = '1.2.0'

def send_html_response(http, title, body, status=httplib.OK):
    http.send_response(status)
    http.send_header('Content-type', 'text/html')
    http.end_headers()
    http.wfile.write(_page_template % (title, body))


def format_properties(properties):
    return _properties_template % ''.join([_property_template % (k, v) for (k, v) in properties.items()])


_page_template = '''
<html>
  <head>
    <title>%s</title>
  </head>
  <body>
%s
  </body>
</html>
'''

_properties_template = '''
<table class='properties'>
%s
</table>
'''

_property_template = '<tr><th>%s</th><td>%s</td></tr>\n'
