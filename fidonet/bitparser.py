import bitstring

from ftnerror import *

class Struct (object):

    def __init__ (self, *fields, **kw):
        self.__fields = {}
        self.__fieldlist = []

        for f in fields:
            self.__fieldlist.append(f)
            self.__fields[f.name] = f

    def parse(self, bits, factory=dict):
        data = factory()

        for f in self.__fieldlist:
            data[f.name] = f.unpack(bits)

        return data

    def build(self, data):
        bitlist = bitstring.BitStream()

        for f in self.__fieldlist:
            bitlist.append(f.pack(data[f.name]))

        return bitlist

    def write(self, data, fd):
        fd.write(self.build(data).bytes)

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

