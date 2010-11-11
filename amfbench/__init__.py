"""
"""

import os.path
import time

from amfbench import builder

binaries = None
base_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'var'))

__all__ = ['encode', 'decode', 'get_blob_filename', 'get_blobs']


def encode(codec, name, size, encoding):
    """
    Uses C{name} to first generate an object graph of C{size} and then uses
    L{codec<amfbench.codec.ICodec} to generate an AMF blob for the given
    encoding type.

    @param name: One of L{builder.builders}
    @param size: The number of objects for the builder to generate.
    @param encoding: The AMF encoding value.
    @return: A tuple containing: the time it took C{codec} to encode the payload
        and the number of bytes that was generated.
    """
    if name not in builder.builders:
        raise NameError('Unknown builder %r' % (name,))

    build_func = getattr(builder, name)
    payload = build_func(size)

    amf3 = False if encoding == 0 else True
    start = time.time()

    try:
        bytes = codec.encode(payload, amf3)
    except Exception, bytes:
        result = None
    else:
        result = time.time() - start

    return result


def decode(codec, name, size, encoding):
    """
    Reads the Flash generated AMF blob from C{base_path} and then uses
    L{codec<amfbench.codec.ICodec} to decode the result.

    @param name: One of L{builder.builders}
    @param size: The number of objects that the builder generated.
    @param encoding: The AMF encoding value.
    @return: The time it took C{codec} to decode the blob. If an error occurred
        whilst decoding the blob then C{None} will be the result.
    """
    if name not in builder.builders:
        raise NameError('Unknown builder %r' % (name,))

    file_name = get_blob_filename(name, size, encoding)

    f = open(file_name, 'rb')
    bytes = f.read()
    f.close()

    amf3 = False if encoding == 0 else True

    start = time.time()

    try:
        payload = codec.decode(bytes, amf3)
    except Exception:
        result = None
    else:
        result = time.time() - start

    return result


def get_blob_filename(builder_name, size, encoding):
    """
    Builds and returns the file name of the amf blob.

    @param builder_name: One of L{builder.builders}
    @param size: The number of objects for the builder
    @param encoding: The AMF encoding value.
    """
    fn = '%s-%d.amf%d' % (builder_name, size, encoding)

    full_path = os.path.abspath(os.path.join(base_path, fn))

    return full_path


def get_blobs():
    """
    Builds a list of available amf blobs in L{base_path}. Each blob has a
    specific name: C{[builder]-[size].amf[version]}
    """
    global binaries

    if binaries:
        return binaries

    files = os.listdir(base_path)

    binaries = {}

    for f in files:
        name, ext = os.path.splitext(f)

        if ext not in ('.amf0', '.amf3'):
            continue

        try:
            t, n = name.split('-')
        except ValueError:
            continue

        d = binaries.setdefault(t, {})

        try:
            x = d.setdefault(int(ext[4]), [])
            x.append(int(n))
        except ValueError:
            continue

        d[int(ext[4])] = sorted(x)

    return binaries
