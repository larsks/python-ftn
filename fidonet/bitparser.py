import bitstring

from ftnerror import *

class Container(dict):

    def __init__(self, struct, *args, **kw):
        super(Container, self).__init__(*args, **kw)
        self.__struct__ = struct

    def __getattr__ (self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    def __setattr__ (self, k,v):
        if hasattr(self.__class__, k) and \
                hasattr(getattr(self.__class__, k), '__set__'):
            super(Container, self).__setattr__(k, v)
        elif k in self:
            self[k] = v
        else:
            super(Container, self).__setattr__(k, v)

    def build(self):
        return self.__struct__.build(self)

class Struct (object):

    def __init__ (self, *fields, **kw):
        self._fields = {}
        self._fieldlist = []

        if 'factory' in kw:
            self.__factory = kw['factory']
        else:
            self.__factory = Container

        for f in fields:
            self._fieldlist.append(f)
            self._fields[f.name] = f

        if 'validate' in kw:
            self._validate = kw['validate']

    def parse(self, bits):
        data = self.__factory(self)
        self.bits = bits

        try:
            for f in self._fieldlist:
                data[f.name] = f.unpack(bits)
        except bitstring.errors.ReadError:
            raise EndOfData

        return data

    def parse_fd(self, fd):
        bits = bitstring.ConstBitStream(fd)
        return self.parse(bits)

    def parse_bytes(self, bytes):
        bits = bitstring.ConstBitStream(bytes=bytes)
        return self.parse(bits)

    def build(self, data):
        bitlist = bitstring.BitStream()

        if hasattr(self, '_validate'):
            self._validate(data)

        for f in self._fieldlist:
            try:
                bitlist.append(f.pack(data[f.name]))
            except KeyError:
                bitlist.append(f.pack(f.default))

        return bitlist

    def write(self, data, fd):
        fd.write(self.build(data).bytes)

    def create(self):
        d = self.__factory(self)

        for f in self._fieldlist:
            if callable(f.default):
                d[f.name] = f.default()
            else:
                d[f.name] = f.default

        return d

class Field (object):
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
    def __init__(self, name, length=None):
        if length:
            spec = 'bits:%d' % length
        else:
            spec = 'bits'
        super(BitStream, self).__init__(name, spec,
                default=_streammaker(length))

class PaddedString(Field):
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
        val = val + self.padchar * self.length [:self.length]
        return super(PaddedString, self).pack(val)
 
