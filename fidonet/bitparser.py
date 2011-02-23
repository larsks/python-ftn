import bitstring

class BitParser (object):
    defaults = {}

    def parse(self, bs):
        fields = {}

        for k,v in self.defaults.items():
            fields[k] = v
        for k, spec in self.format:
            if spec == 'cstring':
                cur = bs.pos
                nul = bs[cur:].find('0x00', bytealigned=True)[0]
                fields[k] = bs[cur:cur+nul].tobytes()
                bs.pos = cur + nul + 8
            else:
                fields[k] = bs.read(spec)

        return fields

    def create(self, **kw):
        fields = []
        for k, spec in self.format:
            fields.append('%s=%s' % (spec, k))

        format = ','.join(fields)
        return bitstring.pack(format, **kw)

