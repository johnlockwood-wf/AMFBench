"""
"""

from amfast.context import DecoderContext, EncoderContext
from amfast import encode, decode, class_def

from amfbench import builder


class Codec(object):
    """
    @implements: amfbench.codec.ICodec
    """

    name = 'AmFast'
    version = '0.4.2'
    package = 'amfast'

    def setUp(self):
        self.class_mapper = class_def.ClassDefMapper()

        self.class_mapper.mapClass(class_def.DynamicClassDef(
            builder.SomeClass,
            builder.aliases[builder.SomeClass],
            (),
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
        enc_context = EncoderContext(use_collections=False, amf3=amf3,
            use_proxies=False, class_def_mapper=self.class_mapper)

        return encode.encode(obj, enc_context)

    def decode(self, bytes, amf3):
        return decode.decode(DecoderContext(bytes,
            class_def_mapper=self.class_mapper, amf3=amf3))
