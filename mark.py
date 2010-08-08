#!/usr/bin/env python
"""
So the idea here is that we get Fl[ash|ex] to encode a set of binaries based
on the builder, size of payload and which encoding version.

This is represented in the C{var/[builder]-[num].amf[version]}

We get each package to decode the results of each binary and then encode the
same payload.
"""

import sys
import os.path
from optparse import OptionParser

import amfbench
from amfbench import codec, builder


class NullStream(object):
    """
    """

    def write(self, msg):
        pass


class Logger(object):
    """
    """

    def __init__(self, stream):
        self.stream = stream

    def log(self, msg):
        self.stream.write(msg + '\n')


def parse_args():
    parser = OptionParser()

    parser.add_option('-e', '--encoding', action='append', dest='encodings',
        choices=('0', '3'))
    parser.add_option('-c', '--codec', action='append', dest='codecs',
        choices=codec.get_available_packages())
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
        default=False)
    parser.add_option('-o', '--out', action='store', dest='output', default=None)

    options, args = parser.parse_args()

    if not args:
        args = builder.builders

    if options.encodings is None:
        options.encodings = [0, 3]
    else:
        for i, e in enumerate(options.encodings):
            options.encodings[i] = int(e)

    if options.codecs is None:
        options.codecs = codec.get_available_packages()

    if not options.verbose:
        options.logger = Logger(NullStream())
    else:
        options.logger = Logger(sys.stderr)

    return options, args


def _bench(options, args, type):
    binaries = amfbench.get_binaries()
    results = {}

    for b in args:
        s = results.setdefault(b, {})

        for encoding in options.encodings:
            n = binaries[b][encoding]
            t = s.setdefault(encoding, {})

            for size in n:
                r = t.setdefault(size, {})

                for c in options.codecs:
                    package = codec.get_codec(c)

                    package.setUp()

                    func = getattr(amfbench, type)

                    r[package.package] = func(package, b, size, encoding)

                    package.tearDown()

    return results


def bench_encoding(options, args):
    return _bench(options, args, 'encode')


def bench_decoding(options, args):
    return _bench(options, args, 'decode')


def write_pickle(options, decode_results, encode_results):
    import cPickle as pickle

    f = None

    # if output is not specified, we dump to stdout
    if options.output:
        f = open(options.output, 'wb')
    else:
        import sys
        f = sys.stdout

    pickle.dump({
        'decode': decode_results,
        'encode': encode_results
    }, f, pickle.HIGHEST_PROTOCOL)


def main():
    options, args = parse_args()

    decode_results = bench_decoding(options, args)
    encode_results = bench_encoding(options, args)

    write_pickle(options, decode_results, encode_results)


if __name__ == '__main__':
    main()
