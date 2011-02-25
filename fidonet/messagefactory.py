import logging

import bitstring

from fidonet.formats import *
from fidonet.ftnerror import *
from message import Message, MessageBodyParser

def MessageFactory(src):
    if isinstance(src, bitstring.BitArray):
        bits = src
    elif hasattr(src, 'read'):
        bits = bitstring.ConstBitStream(src)
    else:
        raise InvalidMessage()

    msg = packedmessage.MessageParser.parse(bits)
    if msg.msgVersion != 2:
        logging.debug('msgVersion != 2; assuming this '
                'is an FTS-0001 (B) message.')
        bits.pos = 0
        msg = diskmessage.MessageParser.parse(bits)
    else:
        logging.debug('msgVersion == 2; assuming this '
                'is an FTS-0001 (C) message.')

    return msg

if __name__ == '__main__':
    import sys
    logging.root.setLevel(logging.DEBUG)
    m = MessageFactory(open(sys.argv[1]))
    print m

