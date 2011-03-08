import os
import sys

required_fields = (
    'AKA',
    'RequestList',
    'ResponseList',
    'RemoteStatus',
    'SystemStatus'
    )

class SRIF (dict):
    def __init__ (self, src, *args, **kw):
        super(SRIF, self).__init__(*args, **kw)
        self.parse(src)
    
    def parse(self, fd):
        for line in (x.strip() for x in fd):
            if not line: continue
            k, v = line.split(None, 1)
            self[k] = v

        for k in required_fields:
            if not k in self:
                raise ValueError('Invalid SRIF file: missing %s' % k)

if __name__ == '__main__':
    import pprint

    d = SRIF(open(sys.argv[1]))
    pprint.pprint(d)
