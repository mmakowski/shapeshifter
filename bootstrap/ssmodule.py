'''
Provides methods for management of Shapeshifter modules.

There is a certain overlap of functionality and duplication of code with 'file' module.
This is to minimise the number of modules required for bootstrapping Shapeshifter.

NOTE: there is currently no provision for any security. Running this module means that anyone
who can connect to the Shapeshifter web server port can execute any code on the machine with
the rights of the user running Shapeshifter.
'''
import cgi
import httplib
import imp
import os
import pydoc

# Shapeshifter modules:
import html

__author__ = 'Maciek Makowski'
__version__ = '1.0.0'


def GET(http, path):
    '''
    If path is None responds with the list of available modules. Otherwise provides a description of the
    module specified in the path.
    '''
    if path == None or len(path) == 0: _list_modules(http)
    else: _describe_module(http, path)


def PUT(http, path):
    '''
    Receives the module sent in the request and makes it available in this Shapeshifter instance under the name
    specified in path. Expected entries in form data:
    - module: the contents of the module
    '''
    mod_name = path
    content = http.data.get('module')
    with open('%s.py' % mod_name, 'wb') as mod_file:
        mod_file.write(content[0])
    _reload_depending_modules(mod_name)
    http.send_response(httplib.CREATED)
    http.send_header('Location', '/ssmodule/%s' % mod_name)
    http.end_headers()


def _list_modules(http):
    module_names = [fn[:-3] for fn in os.listdir('.') if fn.endswith('.py')]
    body = _mod_listing_template % ''.join([_mod_li_template % (mod_name, mod_name) for mod_name in module_names])
    html.send_html_response(http, 'Available Modules', body)


def _describe_module(http, mod_name):
    if mod_name.endswith('.html'): mod_name = mod_name[:-5]
    body = pydoc.html.docmodule(imp.load_source(mod_name, '%s.py' % mod_name))
    html.send_html_response(http, mod_name, body)


def _reload_depending_modules(mod_name):
    '''
    Re-imports all modules which import the module which has just been uploaded.
    TODO
    '''
    pass


_mod_listing_template = '''
    <h1>Available modules</h1>
    <ul class='modules'>
%s
    </ul>
'''

_mod_li_template = '      <li><a href="/ssmodule/%s">%s</a></li>\n'


