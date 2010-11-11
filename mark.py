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
from optparse import OptionParser, OptionGroup

import amfbench
from amfbench import codec, builder


__version__ = (0, 1)
version = '.'.join(map(str, __version__))


class NullStream(object):
    """
    Swallows anything written to this stream. Aka /dev/null
    """

    def write(self, msg):
        pass


class Logger(object):
    """
    Writes log message to a stream.
    """

    def __init__(self, stream):
        self.stream = stream

    def log(self, msg):
        self.stream.write(msg + '\n')


def parse_args(*args):
    """
    Parse and validate command line arguments.
    """
    parser = OptionParser(version='AMFBench %s' % (version,),
        description='Benchmark utility for Python AMF implementations. '
        'Will produce a pickle of timings for the various benchmark types. '
        'To run the decoding benchmarks, make sure you have built the '
        'requisite binaries (Run server.py and browse to localhost:8080).')

    impl = codec.get_available_implementations()
    amf_encodings = ('0', '3')

    parser.add_option('-e', '--encoding', action='append', dest='encodings',
        choices=amf_encodings, help='AMF version/s to benchmark. '
        'Choices are %r. Defaults to all.' % (amf_encodings,))
    parser.add_option('-i', '--implementation', action='append', dest='impl',
        choices=impl,
        help='Python AMF implementation to benchmark. Choices are %r. '
            'Defaults to all.' % (impl,))
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
        default=False, help='Output helpful comments to stderr')
    parser.add_option('-o', '--out', action='store', dest='output',
        default=None, help='Where to write the pickle of benchmark results. '
        'Default is stdout')

    advanced = OptionGroup(parser, "Advanced options")

    advanced.add_option('--only-decode', dest='only_decode',
        action='store_true', help='Only benchmark decoding')
    advanced.add_option('--only-encode', dest='only_encode',
        action='store_true', help='Only benchmark encoding')

    parser.add_option_group(advanced)

    options, args = parser.parse_args()

    if not args:
        args = builder.builders
    else:
        for a in args:
            if a not in builder.builders:
                parser.error("%s is not a valid builder, choose from %r" % (
                    a, builder.builders))

    amf_encodings = tuple(map(int, amf_encodings))

    if options.encodings is None:
        options.encodings = amf_encodings
    else:
        for i, e in enumerate(options.encodings):
            try:
                options.encodings[i] = int(e)
            except ValueError:
                parser.error('%r is not a valid AMF version' % (e,))

    if options.impl is None:
        options.impl = impl
    else:
        for a in options.impl:
            if a not in impl:
                parser.error("%s is not a valid implementation, choose "
                    "from %r" % (a, impl))

    if not options.verbose:
        options.logger = Logger(NullStream())
    else:
        options.logger = Logger(sys.stderr)

    if options.only_decode and options.only_encode:
        parser.error('Conflicting values: only-decode and only-encode. Please '
            'choose one (or neither)')

    return options, args


def _bench(options, args, type):
    binaries = amfbench.get_blobs()
    results = {}

    for b in args:
        s = results.setdefault(b, {})

        for encoding in options.encodings:
            n = binaries[b][encoding]
            t = s.setdefault(encoding, {})

            for size in n:
                r = t.setdefault(size, {})

                for c in options.impl:
                    package = codec.get_implementation(c)

                    package.setUp()

                    func = getattr(amfbench, type)

                    r[package.package] = func(package, b, size, encoding)

                    package.tearDown()

    return results


def bench_encoding(options, args):
    if options.only_decode:
        return {}

    return _bench(options, args, 'encode')


def bench_decoding(options, args):
    if options.only_encode:
        return {}

    return _bench(options, args, 'decode')


def write_pickle(options, decode_results, encode_results):
    import cPickle as pickle

    f = None

    # if output is not specified, we dump to stdout
    if options.output:
        f = open(options.output, 'wb')
    else:
        f = sys.stdout

    pickle.dump({
        'decode': decode_results,
        'encode': encode_results
    }, f, pickle.HIGHEST_PROTOCOL)


def main(*args):
    options, args = parse_args(*args)

    decode_results = bench_decoding(options, args)
    encode_results = bench_encoding(options, args)

    write_pickle(options, decode_results, encode_results)


if __name__ == '__main__':
    main(*sys.argv[1:])
