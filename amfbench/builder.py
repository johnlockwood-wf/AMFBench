# -*- coding: utf-8 -*-

"""
Contains a list of functions that will build object graphs for the codec to
encode.
"""

builders = ['simple', 'complex', 'static', 'reference']

__all__ = builders + ['SomeClass', 'SomeStaticClass']


class BaseObject(object):
    """
    A simple base class for equality checking.
    """

    def __repr__(self):
        return '<%s %r @ 0x%x>' % (
            self.__class__.__name__, self.__dict__, id(self))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return False


class SomeClass(BaseObject):
    """
    A simple class that can contain any attribute that Python supports
    """


class SomeStaticClass(BaseObject):
    """
    A class that will *always* have C{name}, C{score}, C{rank} attributes.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('name', None)
        kwargs.setdefault('score', None)
        kwargs.setdefault('rank', None)

        self.__dict__.update(kwargs)


aliases = {
    SomeClass: 'some.class',
    SomeStaticClass: 'some.static.class'
}


def simple(num):
    """
    Return a list of dicts with some simple data types inserted into it.

    Some points to note:
     * There are no object or string references.

    @param num: The size of the list.
    """
    ret = []

    for i in xrange(0, num):
        test_obj = {
            'number': 10,
            'float': 3.24,
            'string': 'foo number %i' % i,
        }

        ret.append(test_obj)

    return ret


def complex(num):
    """
    Builds a complex object graph with objects references others and more
    complex types (e.g. C{list} and C{dict})

    This builder is a good example of a real world object graph that is
    encoded or decoded.

    Some notes:
     * SomeClass is meant to be typed with alias C{some.class}
    """
    ret = []

    for i in xrange(0, num):
        obj = SomeClass()

        attrs = {
            '_null': None,
            'list': ['test', 'tester'],
            'dict': {'test': 'ignore'},
            'string_ref': 'string reference'
        }

        obj.__dict__.update(attrs)

        obj.number = i
        obj.float = 3.14
        obj.unicode = u'ƒøø'

        obj.sub_obj = SomeClass()
        obj.sub_obj.number = i
        obj.ref = obj.sub_obj

        ret.append(obj)

    return ret


def static(num):
    """
    Returns a list of C{static} objects.

    Some notes:
     * SomeStaticClass is meant to be typed with alias C{some.static.class}
     * There are no object/string references
    """
    ret = []

    for i in xrange(0, num):
        obj = SomeStaticClass()

        attrs = {
            'name': 'name %s' % i,
            'score': 5.5555555,
            'rank': i
        }

        obj.__dict__.update(attrs)

        ret.append(obj)

    return ret


def reference(num, obj=None):
    """
    Returns a list of C{obj} such that each entry in the list is a reference
    to the other. If you don't supply C{obj}, a simple dict will be created.

    This builder is meant to test the raw reference encoding horsepower of the
    codec.
    """
    if obj is None:
        obj = {'foo': 'bar'}

    return [obj] * num
