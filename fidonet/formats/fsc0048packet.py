'''This is the packet format described in FSC-0048_.  This format is a
supserset of FTS-0001, and FSC-0048 describes some heuristics for
determining which format is appropriate for parsing a given packet.

Reading a packet
----------------

Read a packet from a file using the ``parse_fd`` method:

    >>> pkt = PacketParser.parse_fd(open('sample.pkt'))

Accessing packet data
---------------------

You can access packet data as a dictionary:

    >>> pkt['origZone']
    1

Or using dot notation:

    >>> pkt.origZone
    1

Special properties
------------------

The ``origAddr`` and ``destAddr`` properties return the corresponding
address as a ``fidonet.Address`` instance:

    >>> pkt.origAddr.ftn
    '1:322/761'

You can assign an Address object to this property to update the packet:

    >>> from fidonet.address import Address
    >>> pkt.origAddr = Address('1:100/100')
    >>> pkt.origAddr.ftn
    '1:100/100'

The ``time`` method returns a ``time.struct_time`` instance:

    >>> pkt.time
    time.struct_time(tm_year=2011, tm_mon=2, tm_mday=25, tm_hour=21, tm_min=58, tm_sec=17, tm_wday=0, tm_yday=0, tm_isdst=-1)

Assining a ``time.struct_time`` instance will update the packet:

    >>> import time
    >>> pkt.time = time.localtime(1298689930)
    >>> pkt.time
    time.struct_time(tm_year=2011, tm_mon=2, tm_mday=25, tm_hour=22, tm_min=12, tm_sec=10, tm_wday=0, tm_yday=0, tm_isdst=-1)

Writing a packet
----------------

Write a packet to an open file using the ``write`` method:

    >>> pkt.write(open('updated.pkt', 'w'))

.. _FSC-0048: http://www.ftsc.org/docs/fsc-0048.002
'''

from fidonet.bitparser import *
from fidonet.util import fixup_packet
from fidonet.packet import Packet

PacketParser = Struct(
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('year', 'uintle:16'),
            Field('month', 'uintle:16'),
            Field('day', 'uintle:16'),
            Field('hour', 'uintle:16'),
            Field('minute', 'uintle:16'),
            Field('second', 'uintle:16'),
            Field('baud', 'uintle:16'),
            Field('pktVersion', 'uintle:16', default=2),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            Field('productCodeLow', 'uintle:8', default=0xFE),
            Field('productRevMajor', 'uintle:8'),
            Field('password', 'bytes:8', default='\x00' * 8),
            Field('qOrigZone', 'uintle:16'),
            Field('qDestZone', 'uintle:16'),
            Field('auxNet', 'uintle:16'),
            Field('capWordValidationCopy', 'uintbe:16', default=1),
            Field('productCodeHigh', 'uintle:8'),
            Field('productRevMinor', 'uintle:8'),
            Field('capWord', 'uintle:16', default=1),
            Field('origZone', 'uintle:16'),
            Field('destZone', 'uintle:16'),
            Field('origPoint', 'uintle:16'),
            Field('destPoint', 'uintle:16'),
            Field('productData', 'uintle:32'),
            BitStream('messages'),
            Constant('eop', 'bytes:2', '\x00\x00'),

            validate=fixup_packet,
            factory=Packet
            )

if __name__ == '__main__':
    import doctest
    doctest.testmod()

