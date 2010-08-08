"""
AMFBench codec for U{AmFast<http://code.google.com/p/amfast/>}
"""

import amfast
from amfast.context import DecoderContext, EncoderContext
from amfast import encode, decode, class_def

from amfbench import builder


def get_version():
    """
    We have to work round the fact that AmFast does not expose its version
    programmatically until version 0.5.2
    """
    if hasattr(amfast, '__version__'):
        return str(amfast.__version__)

    return 'Unknown'


class Codec(object):
    """
    @implements: L{amfbench.codec.ICodec}
    """

    name = 'AmFast'
    package = amfast.__name__
    version = get_version()

    def setUp(self):
        self.class_mapper = class_def.ClassDefMapper()

        self.class_mapper.mapClass(class_def.DynamicClassDef(
            builder.SomeClass,
            builder.aliases[builder.SomeClass],
            (), # static attrs
            amf3=False))

        self.class_mapper.mapClass(class_def.ClassDef(
            builder.SomeStaticClass,
            builder.aliases[builder.SomeStaticClass],
            ('name', 'score', 'rank'),
            amf3=False))

    def tearDown(self):
        self.class_mapper.unmapClass(builder.SomeClass)
        self.class_mapper.unmapClass(builder.SomeStaticClass)

    def encode(self, obj, amf3):
        context = EncoderContext(use_collections=True, amf3=amf3,
            use_proxies=False, class_def_mapper=self.class_mapper)

        return encode.encode(obj, context)

    def decode(self, bytes, amf3):
        context = DecoderContext(bytes, class_def_mapper=self.class_mapper,
            amf3=amf3)

        return decode.decode(context)
