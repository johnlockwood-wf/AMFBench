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

    parser.add_option('-e', '--encoding', action='append', dest='encodings', choices=('0', '3'))
    parser.add_option('-c', '--codec', action='append', dest='codecs', choices=codec.get_available_packages())
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)

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


def bench_encoding(options, args):
    binaries = amfbench.get_binaries()
    results = {}

    for c in options.codecs:
        package = codec.get_codec(c)

        package.setUp()

        r = results[package.package] = {}

        options.logger.log('Running encoding benchmarks for %s' % (package.name,))

        for b in args:
            s = r.setdefault(b, {})

            for encoding in options.encodings:
                n = binaries[b][encoding]
                t = s.setdefault(encoding, [])

                for size in n:
                    time, payload = amfbench.encode(package, b, size, encoding)

                    t.append((size, time, payload))

                    options.logger.log(' %s %d AMF%d: %s' % (b, size, encoding, time))

        package.tearDown()

    return results


def bench_decoding(options, args):
    binaries = amfbench.get_binaries()
    results = {}

    for c in options.codecs:
        package = codec.get_codec(c)

        package.setUp()

        r = results[package.package] = {}

        options.logger.log('Running decoding benchmarks for %s' % (package.name,))

        for b in args:
            s = r.setdefault(b, {})

            for encoding in options.encodings:
                n = binaries[b][encoding]
                t = s.setdefault(encoding, [])

                for size in n:
                    time, payload = amfbench.decode(package, b, size, encoding)

                    t.append((size, time, payload))

                    options.logger.log(' %s %d AMF%d: %s' % (b, size, encoding, time))

        package.tearDown()

    return results


def csv_results(results):
    import csv

    w = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)

    for package, x in results.iteritems():
        for builder_name, y in x.iteritems():
            for encoding, z in y.iteritems():
                for j in z:
                    n, time, payload = j

                    w.writerow([package, builder_name, encoding, n, time])


def main():
    options, args = parse_args()

    decoding_results = bench_decoding(options, args)
    encoding_results = bench_encoding(options, args)

    csv_results(encoding_results)


if __name__ == '__main__':
    main()
