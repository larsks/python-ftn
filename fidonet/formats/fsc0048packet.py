'''This is the packet format described in FSC-0048_.  This format is a
supserset of FTS-0001, and FSC-0048 describes some heuristics for
determining which format is appropriate for parsing a given packet.

.. _FSC-0048: http://www.ftsc.org/docs/fsc-0048.002
'''

from fidonet.bitparser import *
from fidonet.packet import Packet
from fidonet.formats import packedmessage

PacketParser = Struct('packet',
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('year', 'uintle:16'),
            Field('month', 'uintle:16'),
            Field('day', 'uintle:16'),
            Field('hour', 'uintle:16'),
            Field('minute', 'uintle:16'),
            Field('second', 'uintle:16'),
            Field('baud', 'uintle:16'),
            Constant('pktVersion', 'uintle:16', 2),
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
            factory=Packet,
            )

