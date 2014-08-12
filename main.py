#!/usr/bin/env python
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import SharedDataMiddleware
import psycopg2
import mimetypes
import os
import json


class App(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/recent/<int:count>', endpoint='recent'),
            Rule('/before/<int:before>/<int:count>', endpoint='before'),
            Rule('/after/<int:after>/<int:count>', endpoint='after'),
            Rule('/<filename>.html', endpoint='html'),
            Rule('/js/<filename>', endpoint='js'),
            Rule('/bootstrap/<dir>/<filename>.<extension>', endpoint='bootstrap'),
            ])
        self.connect = psycopg2.connect(dbname='weechat', user='weechat')

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

    def on_recent(self, request, count):
        cursor = self.connect.cursor()
        try:
            query = ("SELECT id, username, servername, channelname, message,"
                     "    hilight, command, time"
                     "  FROM weechat_message"
                     "  ORDER BY id DESC"
                     "  LIMIT %d" % count)
            cursor.execute(query)
            result = cursor.fetchall()
            def to_json(argument):
                (id, username, servername, channelname, message, hilight,
                 command, time) = argument
                return {"id": id, "username": username,
                        "servername": servername, "channelname": channelname,
                        "message": message, "hilight": hilight,
                        "command": command, "time": time.timestamp()}
            result = [to_json(r) for r in result]
            return Response(json.dumps(result),
                            mimetype='application/javascript')
        finally:
            cursor.close()

    def on_before(self, request, before, count):
        cursor = self.connect.cursor()
        try:
            query = ("SELECT id, username, servername, channelname, message,"
                     "    hilight, command, time"
                     "  FROM weechat_message"
                     "  WHERE %d > id"
                     "  ORDER BY id DESC"
                     "  LIMIT %d") % (before, count)
            cursor.execute(query)
            result = cursor.fetchall()
            def to_json(argument):
                (id, username, servername, channelname, message, hilight,
                 command, time) = argument
                return {"id": id, "username": username,
                        "servername": servername, "channelname": channelname,
                        "message": message, "hilight": hilight,
                        "command": command, "time": time.timestamp()}
            result = [to_json(r) for r in result]
            return Response(json.dumps(result),
                            mimetype='application/javascript')
        finally:
            cursor.close()

    def on_after(self, request, after, count):
        cursor = self.connect.cursor()
        try:
            query = ("SELECT id, username, servername, channelname, message,"
                     "    hilight, command, time"
                     "  FROM weechat_message"
                     "  WHERE %d < id"
                     "  ORDER BY id DESC"
                     "  LIMIT %d") % (after, count)
            cursor.execute(query)
            result = cursor.fetchall()
            def to_json(argument):
                (id, username, servername, channelname, message, hilight,
                 command, time) = argument
                return {"id": id, "username": username,
                        "servername": servername, "channelname": channelname,
                        "message": message, "hilight": hilight,
                        "command": command, "time": time.timestamp()}
            result = [to_json(r) for r in result]
            return Response(json.dumps(result),
                            mimetype='application/javascript')
        finally:
            cursor.close()

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
