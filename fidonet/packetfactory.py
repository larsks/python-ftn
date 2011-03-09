import logging

import bitstring

from ftnerror import *
from formats import *
from packet import Packet

def PacketFactory(src):
    if isinstance(src, bitstring.ConstBitArray):
        bits = src
    elif hasattr(src, 'read'):
        bits = bitstring.BitStream(src)
    else:
        raise InvalidPacket()

    try:
        pkt = fsc0045packet.PacketParser.unpack(bits)
        return pkt
    except ValueError:
        bits.pos = 0

    # If we weren't able to parse it as a type 2.2 packet, we'll
    # use the heuristics from FSC-0048 to decide between type 2
    # and type 2+.
    pkt = fsc0048packet.PacketParser.unpack(bits)

    if pkt.pktVersion != 2:
        logging.error('pktVersion != 2')
        raise InvalidPacket()

    if pkt.capWord != pkt.capWordValidationCopy \
            or pkt.capWord == 0 \
            or pkt.capWord & 0x01 == 0:
        logging.debug('capWord check indicates this '
                'is an fts-0001 packet.')
        bits.pos = 0
        pkt = fts0001packet.PacketParser.unpack(bits)

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

