"""
AMFBench codec for SimpleJSON
"""

import simplejson

from amfbench import builder


class Codec(object):
    """
    @implements: L{amfbench.codec.ICodec}
    """

    name = 'SimpleJSON'
    package = simplejson.__name__
    version = str(simplejson.__version__)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def encode(self, payload, amf3):
        return simplejson.dumps(payload)

    def decode(self, bytes, amf3):
        return simplejson.loads(bytes)
