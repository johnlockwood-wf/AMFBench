"""
AMFBench codec for U{cPickle<http://docs.python.org/library/pickle.html>}
"""

import cPickle

from amfbench import builder


class Codec(object):
    """
    @implements: L{amfbench.codec.ICodec}
    """

    name = 'cPickle'
    package = cPickle.__name__
    version = str(cPickle.__version__)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def encode(self, payload, amf3):
        return cPickle.dumps(payload)

    def decode(self, bytes, amf3):
        return cPickle.loads(bytes)
