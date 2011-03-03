import logging

import bitstring

from fidonet.formats import *
from fidonet.ftnerror import *
from message import Message, MessageBodyParser

def MessageFactory(src):
    if isinstance(src, bitstring.ConstBitArray):
        bits = src
    elif hasattr(src, 'read'):
        bits = bitstring.BitStream(src)
    else:
        raise InvalidMessage()

    mark = bits.pos
    msg = packedmessage.MessageParser.unpack(bits)
    if msg.msgVersion != 2:
        logging.debug('msgVersion != 2; assuming this '
                'is an FTS-0001 (B) message.')
        bits.pos = mark
        msg = diskmessage.MessageParser.unpack(bits)
    else:
        logging.debug('msgVersion == 2; assuming this '
                'is an FTS-0001 (C) message.')

    return msg

if __name__ == '__main__':
    import sys
    logging.root.setLevel(logging.DEBUG)
    m = MessageFactory(open(sys.argv[1]))
    print m

