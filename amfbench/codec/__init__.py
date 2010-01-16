"""
"""

class ICodec:
    """
    Provides a unified interface to working with various AMF implementations

    @ivar name: The printable name of the codec (e.g. PyAMF)
    @ivar package: The package name for the project (e.g. amfast)
    @ivar version: The stringified version of the codec (e.g. 0.4.2)
    """

    def setUp(self):
        """
        Prepare the codec for action. Called when an encode/decode operation
        is about to be performed.
        """

    def tearDown(self):
        """
        Opposite of L{setUp}. Called when an encode/decode operation has been
        completed.
        """

    def encode(self, payload, amf3):
        """
        Encodes the C{payload}, returning the raw bytes.

        @param payload: The object graph to encode.
        @param amf3: A boolean determining whether or not to encode in AMF3.
            If this value is C{False} then AMF0 should be used.
        @return: The bytes produced in the encode operation.
        """

    def decode(self, bytes, amf3):
        """
        Decodes the C{bytes} and returns the result.

        @param bytes: The raw bytes to .
        @param amf3: A boolean determining whether or not to encode in AMF3.
            If this value is C{False} then AMF0 should be used.
        @return: The bytes produced in the encode operation.
        """


def get_codec(name):
    """
    Returns a ICodec instance for C{name}.

    @raise NameError: C{name} is not a valid codec implementation
    """
    full_name = '%s._%s' % (__name__, name)

    try:
        mod = __import__(full_name)
    except ImportError:
        raise NameError('%r not an available codec' % (name,))

    for part in full_name.split('.')[1:]:
        mod = getattr(mod, part)

    kls = mod.Codec

    return kls()
