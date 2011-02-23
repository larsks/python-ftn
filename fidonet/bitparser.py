import bitstring

class Struct (dict):
    def __init__(self, *fields):
        self.fieldlist = []
        for field in fields:
            c = field.copy()
            self[field.name] = c
            self.fieldlist.append(c)

    def __getattr__ (self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    def parse_fd(self, fd):
        bits = bitstring.ConstBitStream(fd)
        return self.parse(bits)

    def parse_string(self, s):
        bits = bitstring.ConstBitStream(bytes=s)
        return self.parse(bits)

    def parse(self, bits):
        s = Struct(*self.fieldlist)
        for field in self.fieldlist:
            s[field.name].unpack(bits)

        return s

    def _bits(self):
        b = bitstring.BitStream()
        for field in self.fieldlist:
            b.append(field.pack())

        return b

    bits = property(_bits)

    def create(self):
        s = Struct(*self.fieldlist)
        return s

    def write(self, fd):
        fd.write(self.bits.bytes)

class Field (object):
    def __init__ (self, name, spec, transform=None, default=0):
        self.name = name
        self.spec = spec
        self.transform = transform
        self.default = default
        self._val = default

    def __repr__ (self):
        return '<Field "%s" (%s)>' % (self.name, self.spec)

    def __str__ (self):
        return str(self._val)

    def copy(self):
        return Field(self.name, self.spec, self.transform, self.default)

    def get(self):
        return self._val

    def set(self, v):
        if callable(self.transform):
            self._val = self.transform(v)
        else:
            self._val = v

#        print 'SET %s = %s' % (self.name, self._val)

    val = property(get, set)

    def unpack(self, bits):
        self.set(bits.read(self.spec))

    def pack(self):
        return bitstring.pack(self.spec, self._val)

class CString(Field):
    def __init__ (self, name, transform=None, default=None):
        super(CString, self).__init__(name, 'cstring', transform, default)

    def unpack(self, bits):
        cur = bits.pos
        nul = bits[cur:].find('0x00', bytealigned=True)[0]
        v = bits[cur:cur+nul].tobytes()
        bits.pos = cur + nul + 8

        self.set(v)

    def pack(self):
        return bitstring.pack('bytes, 0x00', self._val)

    def copy(self):
        return CString(self.name, self.transform, self.default)

