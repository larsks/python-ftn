import os
import sys
import bitstring
import time

from ftnerror import *
from util import *
from formats import *

from bitparser import Container
from address import Address

class Packet (Container):

    origAddr = ftn_address_property('orig')
    destAddr = ftn_address_property('dest')

    def _get_time (self):
        return time.struct_time([
            self.year, self.month+1, self.day,
            self.hour, self.minute, self.second,
            0, 0, -1])

    def _set_time(self, t):
        self.year = t.tm_year
        self.month = t.tm_mon-1
        self.day = t.tm_mday
        self.hour = t.tm_hour
        self.minute = t.tm_min
        self.second = t.tm_sec

    time = property(_get_time, _set_time)

def PacketFactory(bits=None, fd=None):
    if bits is None:
        bits = bitstring.ConstBitStream(fd)

    pkt = fsc0048packet.PacketParser.parse(bits, factory=Packet)

    # Heuristics from FSC-0048:
    # http://www.ftsc.org/docs/fsc-0048.002
    if pkt.pktVersion != 2:
        raise InvalidPacket()

    if pkt.capWord != pkt.capWordValidationCopy \
            or pkt.capWord == 0 \
            or pkt.capWord & 0x01 == 0:
        bits.pos = 0
        pkt = fts0001packet.PacketParser.parse(bits, factory=Packet)

    return pkt

if __name__ == '__main__':
    p = PacketFactory(fd=open(sys.argv[1]))

    print '=' * 70
    print '%(origZone)s:%(origNet)s/%(origNode)s ->' % p,
    print '%(destZone)s:%(destNet)s/%(destNode)s' % p,
    print '@ %(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s' % p
    print '=' * 70
    print

