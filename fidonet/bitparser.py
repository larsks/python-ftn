import bitstring

from ftnerror import *

class Container(dict):

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

class Struct (object):

    def __init__ (self, *fields, **kw):
        self.__fields = {}
        self.__fieldlist = []

        if 'factory' in kw:
            self.__factory = kw['factory']
        else:
            self.__factory = Container

        if 'validate' in kw:
            self.__validate = kw['validate']

        for f in fields:
            self.__fieldlist.append(f)
            self.__fields[f.name] = f

    def parse(self, bits):
        data = self.__factory()

        try:
            for f in self.__fieldlist:
                data[f.name] = f.unpack(bits)
        except bitstring.errors.ReadError:
            raise EndOfData()

        return data

    def parse_fd(self, fd):
        bits = bitstring.ConstBitStream(fd)
        return self.parse(bits)

    def parse_bytes(self, bytes):
        bits = bitstring.ConstBitStream(bytes=bytes)
        return self.parse(bits)

    def build(self, data):
        bitlist = bitstring.BitStream()

        if hasattr(self, '__validate'):
            self.__validate(data)

        for f in self.__fieldlist:
            bitlist.append(f.pack(data[f.name]))

        return bitlist

    def write(self, data, fd):
        fd.write(self.build(data).bytes)

    def create(self):
        d = self.__factory()

        for f in self.__fieldlist:
            d[f.name] = f.default

        return d

class Field (object):
    def __init__ (self, name, spec=None, transform=None, default=0):
        self.name = name
        self.spec = spec
        self.transform = transform
        self.default = default

    def __repr__ (self):
        return '<Field "%s" (%s)>' % (self.name, self.spec)

    def unpack(self, bits):
        return bits.read(self.spec)

    def pack(self, val):
        return bitstring.pack(self.spec, val)

class CString(Field):
    def __init__ (self, *args, **kwargs):
        super(CString, self).__init__(*args, **kwargs)
        self.spec = 'bytes, 0x00'

    def unpack(self, bits):
        cur = bits.pos
        nul = bits[cur:].find('0x00', bytealigned=True)[0]
        v = bits[cur:cur+nul].tobytes()
        bits.pos = cur + nul + 8

        return v

