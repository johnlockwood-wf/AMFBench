"""
"""

import os.path
import time

from amfbench import builder

binaries = None

def _get_file(builder_name, size, encoding):
    fn = '%s-%d.amf%d' % (builder_name, size, encoding)

    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'var', fn))

    if not os.path.isfile(full_path):
        return None

    return full_path


def get_binaries():
    global binaries

    if binaries:
        return binaries

    files = os.listdir(os.path.join(os.path.dirname(__file__), '..', 'var'))

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


def encode(codec, builder_name, size, encoding):
    """
    """
    try:
        build_func = getattr(builder, builder_name)
    except AttributeError:
        raise NameError('Unknown builder')

    payload = build_func(size)

    amf3 = False if encoding == 0 else True
    start = time.time()

    try:
        bytes = codec.encode(payload, amf3)
    except Exception, bytes:
        result = None
    else:
        result = time.time() - start

    return result, len(bytes)


def decode(codec, builder_name, size, encoding):
    """
    """
    file_name = _get_file(builder_name, size, encoding)

    f = open(file_name, 'rb')
    bytes = f.read()
    f.close()

    amf3 = False if encoding == 0 else True

    start = time.time()

    try:
        payload = codec.decode(bytes, amf3)
    except Exception, payload:
        result = None
    else:
        result = time.time() - start

    return result, payload
