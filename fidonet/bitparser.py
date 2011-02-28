'''The ``bitparser`` module is a wrapper around bitstring_ that allows
you to define data structures using a simple (I hope) declarative syntax.
The syntax was inspired by the abandoned construct_ module.

.. _bitstring: http://code.google.com/p/python-bitstring/
.. _construct: http://construct.wikispaces.com/
'''

import sys
import logging
import bitstring

from ftnerror import *

class Container(dict):
    '''The ``Struct`` class returns ``Container`` instances when you call any
    of the ``parse`` methods.'''

    def __init__(self, struct, *args, **kw):
        super(Container, self).__init__(*args, **kw)
        self.__struct__ = struct

    def __getattr__ (self, k):
        '''Allow keys to be accessed using dot notation.'''
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    def __setattr__ (self, k,v):
        '''Allow keys to be set using dot notation.'''
        if hasattr(self.__class__, k) and \
                hasattr(getattr(self.__class__, k), '__set__'):
            super(Container, self).__setattr__(k, v)
        elif k in self:
            self[k] = v
        else:
            super(Container, self).__setattr__(k, v)

    def __getitem__ (self, k):
        '''Make properties accessible as keys.'''
        try:
            return super(Container, self).__getitem__(k)
        except KeyError:
            if hasattr(self.__class__, k) and \
                    isinstance(getattr(self.__class__, k), property):
                return getattr(self, k)
            else:
                raise

    def build(self):
        '''Return the binary representation of this object as a
        BitStream.'''
        return self.__struct__.build(self)

    def write(self, fd):
        '''Write the binary representation of this object to a file.'''
        return self.__struct__.write(self, fd)

    def __parse__ (self):
        '''This method is called by Struct.parse() after processing all of
        the field defintions.  This allows a wrapper object to extract data
        that otherwise cannot be parsed by the low-level parser.'''

    def __build__ (self):
        '''This method is called by Struct.build() immediately before
        processing all the field definitions.  This allows a wrapper object
        to encode data that otherwse cannot be encoded by the low-level
        parser.'''

class Struct (object):

    def __init__ (self, *fields, **kw):
        '''Create a new Struct instance.

        - ``fields`` -- a list of ``Field`` instances that define the data
          structure.

        You may also pass the following keyword arguments:

        - ``factory`` -- controls the class return by the ``parse``
          methods.  This should generally be a ``Container`` instance.
        '''

        self._fields = {}
        self._fieldlist = []

        if 'factory' in kw:
            self.__factory = kw['factory']
        else:
            self.__factory = Container

        for f in fields:
            self._fieldlist.append(f)
            self._fields[f.name] = f

    def parse(self, bits):
        '''Parse a binary stream into a structured format.'''

        data = self.__factory(self)
        self.bits = bits

        try:
            for f in self._fieldlist:
                data[f.name] = f.unpack(bits)
        except bitstring.errors.ReadError:
            raise EndOfData

        if hasattr(data, '__parse__'):
            data.__parse__()

        return data

    def parse_fd(self, fd):
        '''Parse binary data from an open file into a structured format.'''

        bits = bitstring.ConstBitStream(fd)
        return self.parse(bits)

    def parse_bytes(self, bytes):
        '''Parse a sequence of bytes into a structued format.'''

        bits = bitstring.ConstBitStream(bytes=bytes)
        return self.parse(bits)

    def build(self, data):
        '''Transform a structured format into a binrary representation.'''

        bits = bitstring.BitStream()

        if hasattr(data, '__build__'):
            data.__build__()

        for f in self._fieldlist:
            logging.debug('packing field %s as "%s"' % (f.name, f.spec))
            try:
                bits.append(f.pack(data[f.name]))
            except KeyError:
                bits.append(f.pack(f.default))

        return bits

    def write(self, data, fd):
        '''Write the binary representation of a structured format to an
        open file.'''

        fd.write(self.build(data).bytes)

    def create(self):
        '''Return an empty Container instance corresponding to this
        Struct.'''

        data = self.__factory(self)

        for f in self._fieldlist:
            if callable(f.default):
                data[f.name] = f.default()
            else:
                data[f.name] = f.default

        if hasattr(data, '__parse__'):
            data.__parse__()

        return data

class Field (object):
    '''Represents a field in a binary structure.'''

    def __init__ (self, name, spec=None, default=0):

        self.name = name
        self.spec = spec
        self.default = default

    def unpack(self, bits):
        return self.__unpack(bits)

    def pack(self, val):
        return bitstring.pack(self.spec, self.__pack(val))

    def __unpack(self, bits):
        return bits.read(self.spec)

    def __pack(self, val):
        return val

class CString(Field):
    '''A NUL-terminated string.'''

    def __init__ (self, *args, **kw):
        super(CString, self).__init__(*args, **kw)
        self.spec = 'bytes, 0x00'

    def unpack(self, bits):
        cur = bits.pos
        nul = bits[cur:].find('0x00', bytealigned=True)[0]
        v = bits[cur:cur+nul].tobytes()
        bits.pos = cur + nul + 8

        return v

def _streammaker(length):
    def _():
        return bitstring.BitStream(length)
    return _

class BitStream(Field):
    '''A BitStream.  If length is unspecified, consumes all the remaining
    bytes in the stream, otherwise this is a bit field of the given
    length.'''

    def __init__(self, name, length=None):
        if length:
            spec = 'bits:%d' % length
        else:
            spec = 'bits'
        super(BitStream, self).__init__(name, spec,
                default=_streammaker(length))

class PaddedString(Field):
    '''A fixed-width string filled with a padding character.'''

    def __init__(self, name, length=0, padchar=' ', **kw):
        super(PaddedString, self).__init__(name, 'bytes:%d' % length,
                default=padchar * length)
        self.length = length
        self.padchar = padchar

    def unpack(self, bits):
        v = super(PaddedString, self).unpack(bits)
        v.rstrip(self.padchar)

        return v

    def pack(self, val):
        val = (val + self.padchar * self.length) [:self.length]
        return super(PaddedString, self).pack(val)
 
class Constant(Field):
    '''A constant field.'''

    def __init__(self, name, spec, val):
        super(Constant, self).__init__(name, spec, val)
        self.val = val

    def unpack(self, bits):
        '''Advance the bit position but ignore the read bits and return a
        constant value.'''
        return self.val

    def pack(self, val):
        return super(Constant, self).pack(self.val)

