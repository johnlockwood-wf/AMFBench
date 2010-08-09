"""
Provides a simple AMF remoting gateway that will strip the remoting wrapper and
dump the raw payload. Use in conjunction with C{amfbench/flex/main.swf}
"""

import os
import sys
import logging
from optparse import OptionParser
import struct

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
                ('Content-Length', str(len(bytes)))
            ])

            return [self.xml]

        return self.app(environ, start_response)


class ServeSWF(BaseMiddleware):
    """
    """

    swf_file = 'flex/main.swf'
    url = '/'
    content_type = 'application/x-shockwave-flash'

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == self.url:
            try:
                f = open(self.swf_file, 'rb')
            except:
                start_response('404 Not Found', [])

                return []

            bytes = f.read()

            start_response('200 OK', [
                ('Content-Type', self.content_type),
                ('Content-Length', str(len(bytes)))
            ])

            return [bytes]

        return self.app(environ, start_response)


def handle_request(environ, start_response):
    """
    Strips the AMF remoting wrapper from the request and dumps it to a file
    determined by the service request method and version.

    @see: L{amfbench.get_blob_filename}
    """
    bytes = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))

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

    f = open(amfbench.get_blob_filename(builder_name, int(size), amf_version), 'wb')

    f.write(bytes)
    f.flush()
    f.close()

    # return an empty success response
    ret = '\x00\x00\x00\x00\x00\x01'

    s = '%s/onResult' % (uid,)

    ret += struct.pack('!H', len(s))
    ret += s

    ret += '\x00\x04null\x00\x00\x00\x00\x05'

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


def parse_options():
    parser = build_argparse()

    return parser.parse_args()


def get_app(options):
    app = ServeSWF(CrossdomainMiddleware(handle_request))

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
