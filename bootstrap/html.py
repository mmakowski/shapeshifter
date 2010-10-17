'''
Provides functions and templates for generating HTML reponses.
'''
import httplib

__author__ = 'Maciek Makowski'
__version__ = '1.1.0'

def send_html_response(http, title, body, status=httplib.OK):
    http.send_response(status)
    http.send_header('Content-type', 'text/html')
    http.end_headers()
    http.wfile.write(page_template % (title, body))

page_template = '''
<html>
  <head>
    <title>%s</title>
  </head>
  <body>
%s
  </body>
</html>
'''
