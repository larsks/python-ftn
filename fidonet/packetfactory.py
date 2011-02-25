import logging

import bitstring

from ftnerror import *
from formats import *
from packet import Packet

def PacketFactory(src):
    if isinstance(src, bitstring.ConstBitArray):
        bits = src
    elif hasattr(src, 'read'):
        bits = bitstring.ConstBitStream(src)
    else:
        raise InvalidPacket()

    pkt = fsc0048packet.PacketParser.parse(bits)

    # Heuristics from FSC-0048:
    # http://www.ftsc.org/docs/fsc-0048.002
    if pkt.pktVersion != 2:
        logging.error('pktVersion != 2')
        raise InvalidPacket()

    if pkt.capWord != pkt.capWordValidationCopy \
            or pkt.capWord == 0 \
            or pkt.capWord & 0x01 == 0:
        logging.debug('capWord check indicates this '
                'is an fts-0001 packet.')
        bits.pos = 0
        pkt = fts0001packet.PacketParser.parse(bits)

    return pkt

if __name__ == '__main__':
    import sys

    p = PacketFactory(open(sys.argv[1]))

    print '=' * 70
    print '%(origZone)s:%(origNet)s/%(origNode)s ->' % p,
    print '%(destZone)s:%(destNet)s/%(destNode)s' % p,
    print '@ %(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s' % p
    print '=' * 70
    print

