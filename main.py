#!/usr/bin/env python
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import SharedDataMiddleware
import mimetypes
import os


class App(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/<filename>.html', endpoint='html'),
            Rule('/js/<filename>', endpoint='js'),
            Rule('/bootstrap/<dir>/<filename>.<extension>', endpoint='bootstrap'),
            ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        return getattr(self, 'on_' + endpoint)(request, **values)

    def on_root(self, request):
        self.on_html(request, 'index')

    def on_html(self, request, filename):
        path = os.path.join(os.path.dirname(__file__), 'html')
        filepath = os.path.join(path, filename + '.html')
        file = open(filepath, 'rb')
        content = file.read()
        file.close()
        return Response(content, mimetype='text/html')

    def on_js(self, request, filename):
        path = os.path.join(os.path.dirname(__file__), 'js')
        filepath = os.path.join(path, filename)
        file = open(filepath, 'rb')
        content = file.read()
        file.close()
        return Response(content, mimetype='application/javascript')

    def on_bootstrap(self, request, dir, filename, extension):
        path = os.path.join(os.path.dirname(__file__), 'bootstrap', dir)
        filepath = os.path.join(path, filename + '.' + extension)
        file = open(filepath, 'rb')
        content = file.read()
        file.close()
        mimetype = 'font/opentype'
        if extension == 'css':
            mimetype = 'text/css'
        elif extension == 'js':
            mimetype = 'application/javascript'
        return Response(content, mimetype=mimetype)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


if __name__ == '__main__':
    app = App()
    run_simple('ocean.seulgik.im', 5000, app,
               use_debugger=True, use_reloader=True)
