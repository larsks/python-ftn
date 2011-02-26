'''A wrapper class for FTN packets.

Reading a packet
----------------

Read a packet from a file using the ``fidonet.PacketFactory``
method:

    >>> import fidonet
    >>> pkt = fidonet.PacketFactory(open('tests/sample.pkt'))

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
'''

import os
import sys
import bitstring
import time

from ftnerror import *
from util import *
from bitparser import Container

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

    def __str__ (self):
        text = [
                '%s -> %s @ %s' % (
                    self.origAddr, self.destAddr,
                    time.strftime('%Y-%m-%d %T', self.time))
        ]

        return '\n'.join(text)

