"""
Provides a simple AMF remoting gateway that will strip the remoting wrapper and
dump the raw payload. Use in conjunction with C{amfbench/flex/main.swf}
"""

import os
import sys
import logging
from optparse import OptionParser
import struct
import mimetypes

import amfbench


class BaseMiddleware(object):
    """
    @ivar app: The WSGI application that this middleware component wraps.
    """

    def __init__(self, app):
        self.app = app


class CrossdomainMiddleware(BaseMiddleware):
    """
    Responds to '/crossdomain.xml' requests
    """

    xml = ('<?xml version="1.0"?><cross-domain-policy>'
        '<allow-access-from domain="*" to-ports="*" secure="false"/>'
        '</cross-domain-policy>')

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == '/crossdomain.xml':
            start_response('200 OK', [
                ('Content-Type', 'application/xml'),
                ('Content-Length', str(len(self.xml)))
            ])

            return [self.xml]

        return self.app(environ, start_response)


class ServeStatic(BaseMiddleware):
    """
    Serves static files.
    """

    def __init__(self, app, dir_name, url_root):
        BaseMiddleware.__init__(self, app)

        self.dir_name = os.path.abspath(dir_name)
        self.url_root = url_root

        mimetypes.init()

    def __call__(self, environ, start_response):
        if not environ['PATH_INFO'].startswith(self.url_root):
            return self.app(environ, start_response)

        file_name = environ['PATH_INFO'][len(self.url_root):]

        full_path = os.path.abspath(os.path.join(self.dir_name, file_name))

        if not os.path.isfile(full_path):
            return self.app(environ, start_response)

        f = open(full_path, 'rb')

        ext = os.path.splitext(full_path)[1]
        bytes = f.read()

        start_response('200 OK', [
            ('Content-Type', mimetypes.types_map[ext]),
            ('Content-Length', str(len(bytes)))
        ])

        return [bytes]


class DecodingGeneratorGateway(BaseMiddleware):
    """
    Accepts Flash Remoting requests and dumps it to a named file, returning a
    dummy response.
    """

    url = '/gw'

    @staticmethod
    def strip_envelope(bytes):
        amf_version = struct.unpack('!H', bytes[:2])[0]

        assert bytes[2:6] == '\x00\x00\x00\x01'
        l = struct.unpack('!H', bytes[6:8])[0]

        service_method = bytes[8:l+8]
        bytes = bytes[l+8:]

        l = struct.unpack('!H', bytes[0:2])[0]
        uid = bytes[2:l+2]

        bytes = bytes[l+2:]

        if amf_version == 0:
            boundary = '\n\x00\x00\x00\x01'
        elif amf_version == 3:
            boundary = '\x00\x00\x00\x01\x11'
        else:
            raise RuntimeError('Unknown AMF type')

        bytes = bytes[bytes.find(boundary) + len(boundary):]

        builder_name, size = service_method.split('-')

        return builder_name, size, amf_version, uid, bytes

    @staticmethod
    def generate_response(uid):
        # return an empty success response
        ret = '\x00\x00\x00\x00\x00\x01'

        s = '%s/onResult' % (uid,)

        ret += struct.pack('!H', len(s))
        ret += s

        ret += '\x00\x04null\x00\x00\x00\x00\x05'

        return ret

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] != self.url:
            return self.app(environ, start_response)

        if environ.get('REQUEST_METHOD', 'GET') == 'GET':
            start_response('400 Bad Request', [])

            return ['This gateway only accepts POST requests']

        bytes = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))

        builder_name, size, amf_version, uid, bytes = self.strip_envelope(bytes)

        f = open(amfbench.get_blob_filename(
            builder_name, int(size), amf_version), 'wb')

        f.write(bytes)
        f.flush()
        f.close()

        del f

        ret = self.generate_response(uid)

        # flash doesn't respond to 204 :-/
        start_response('200 OK', [
            ('Content-Length', str(len(ret))),
            ('Content-Type', 'application/x-amf')
        ])

        return [ret]


def build_argparse():
    parser = OptionParser()

    parser.add_option("--iface", default='127.0.0.1', dest='iface',
        help='The network interface to bind to. Supply 0.0.0.0 for all')
    parser.add_option("--port", default=8080, type='int', dest='port',
        help='The port to bind to.')

    return parser


class Redirector(BaseMiddleware):
    """
    Redirects from one url to another
    """

    def __init__(self, app, url_from, url_to):
        BaseMiddleware.__init__(self, app)

        self.url_from = url_from
        self.url_to = url_to

    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO', None) != self.url_from:
            return self.app(environ, start_response)

        start_response('302 Moved Temporarily', [
            ('Location', self.url_to)
        ])

        return []


def parse_options():
    parser = build_argparse()

    return parser.parse_args()


def get_app(options):
    def four_oh_four(environ, start_response):
        start_response('404 Not Found', [])

        return ['<html><body><h1>404 Not Found</h1></body></html>']

    app = four_oh_four
    app = Redirector(app, '/', '/static/AMFBench.html')
    app = CrossdomainMiddleware(app)
    app = DecodingGeneratorGateway(app)
    app = ServeStatic(app, 'static', '/static/')

    return app


def run_server(options):
    from wsgiref import simple_server

    httpd = simple_server.WSGIServer(
        (options.iface, options.port),
        simple_server.WSGIRequestHandler,
    )

    httpd.set_app(get_app(options))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import server

    options, args = parse_options()

    server.run_server(options)
