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

