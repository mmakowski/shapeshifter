'''
Provides functions and templates for generating HTML reponses.
'''
import httplib

__author__ = 'Maciek Makowski'
__version__ = '0.0.1'

def send_html_response(http, title, body):
    http.send_response(httplib.OK)
    http.send_header('Content-type', 'text/html')
    http.end_headers()
    http.wfile.write(page_template % (title, body))

page_template = '''
<html>
  <head>
    <title>%s</title>
  </head>
  <body>huhu!!!
%s
  </body>
</html>
'''
