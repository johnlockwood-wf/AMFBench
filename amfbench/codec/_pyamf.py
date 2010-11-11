"""
AMFBench codec for U{PyAMF<http://pyamf.org/>}
"""

import pyamf

from amfbench import builder


class Codec(object):
    """
    @implements: L{amfbench.codec.ICodec}
    """

    name = 'PyAMF'
    package = pyamf.__name__
    version = str(pyamf.__version__)

    def setUp(self):
        a = pyamf.register_class(builder.SomeClass,
            builder.aliases[builder.SomeClass])

        a.compile()

        builder.SomeStaticClass.__amf__ = {
            'dynamic': False,
            'static': ('name', 'score', 'rank')
        }

        a = pyamf.register_class(builder.SomeStaticClass,
            builder.aliases[builder.SomeStaticClass])

        a.compile()

    def tearDown(self):
        pyamf.unregister_class(builder.SomeClass)
        pyamf.unregister_class(builder.SomeStaticClass)

        del builder.SomeStaticClass.__amf__

    def encode(self, payload, amf3):
        encoding = pyamf.AMF3 if amf3 else pyamf.AMF0

        return pyamf.encode(payload, encoding=encoding).getvalue()

    def decode(self, bytes, amf3):
        encoding = pyamf.AMF3 if amf3 else pyamf.AMF0

        return list(pyamf.decode(bytes, encoding=encoding))
