import os
import sys
import bitstring

from ftnerror import *
from bitparser import BitParser

class fts0001 (BitParser):
    format = (
            ('origNode', 'uintle:16'),
            ('destNode', 'uintle:16'),
            ('year', 'uintle:16'),
            ('month', 'uintle:16'),
            ('day', 'uintle:16'),
            ('hour', 'uintle:16'),
            ('minute', 'uintle:16'),
            ('second', 'uintle:16'),
            ('baud', 'uintle:16'),
            ('pktVersion', 'uintle:16'),
            ('origNet', 'uintle:16'),
            ('destNet', 'uintle:16'),
            ('productCodeLow', 'uintle:8'),
            ('serialNo', 'uintle:8'),
            ('password', 'bits:64'),
            ('qOrigZone', 'uintle:16'),
            ('qDestZone', 'uintle:16'),
            ('fill', 'bits:160'),
            )

class fsc0048 (BitParser):
    defaults = {
            'serialNo': 0,
            'fill': bitstring.BitString(80),
            }

    format = (
            ('origNode', 'uintle:16'),
            ('destNode', 'uintle:16'),
            ('year', 'uintle:16'),
            ('month', 'uintle:16'),
            ('day', 'uintle:16'),
            ('hour', 'uintle:16'),
            ('minute', 'uintle:16'),
            ('second', 'uintle:16'),
            ('baud', 'uintle:16'),
            ('pktVersion', 'uintle:16'),
            ('origNet', 'uintle:16'),
            ('destNet', 'uintle:16'),
            ('productCodeLow', 'uintle:8'),
            ('productRevMajor', 'uintle:8'),
            ('password', 'bits:64'),
            ('qOrigZone', 'uintle:16'),
            ('qDestZone', 'uintle:16'),
            ('auxNet', 'uintle:16'),
            ('capWordValidationCopy', 'uintbe:16'),
            ('productCodeHigh', 'uintle:8'),
            ('productRevMinor', 'uintle:8'),
            ('capWord', 'uintle:16'),
            ('origZone', 'uintle:16'),
            ('destZone', 'uintle:16'),
            ('origPoint', 'uintle:16'),
            ('destPoint', 'uintle:16'),
            ('productData', 'uintle:32'),
            )

class Packet (object):
    def parse(self, bits=None, fd=None):
        if bits is None:
            bits = bitstring.Bits(fd)

        parser = fsc0048()
        fields = parser.parse(bits)

        # Heuristics from FSC-0048:
        # http://www.ftsc.org/docs/fsc-0048.002
        if fields['pktVersion'] != 2:
            raise InvalidPacket()

        if fields['capWord'] != fields['capWordValidationCopy']:
            self.fts = 'FTS-0001 [capWord does not match]'
            bits.pos = 0
            fields = fts0001().parse(bits)
        elif fields['capWord'] == 0:
            self.fts = 'FTS-0001 [capWord is 0]'
            bits.pos = 0
            fields = fts0001().parse(bits)
        elif fields['capWord'] & 0x01 == 0:
            self.fts = 'FTS-0001 [capWord indicates no support for 2+ packets]'
            bits.pos = 0
            fields = fts0001().parse(bits)
        else:
            # This is an FSC-0048 packet.
            self.fts = 'FSC-0048'

        self.fields = fields
        self.bits = bits

if __name__ == '__main__':
    from message import Message

    p = Packet()
    m = Message()

    for f in sys.argv[1:]:
        p.parse(fd=open(f))
        print '%(origZone)s:%(origNet)s/%(origNode)s ->' % p.fields,
        print '%(destZone)s:%(destNet)s/%(destNode)s' % p.fields,
        print '@ %(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s' % p.fields
        print
        count = 0
        while True:
            try:
                m.parse(p.bits)
                print '[%03d]' % count,
                print 'From: %(fromUsername)s @ %(origNet)s/%(origNode)s' % m.fields
                print '      To: %(toUsername)s @ %(destNet)s/%(destNode)s' % m.fields
                print '      Subject: %(subject)s' % m.fields
                print '-' * 70
                count += 1
            except bitstring.errors.ReadError:
                break

