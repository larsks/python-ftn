import os
import sys
import bitstring

from ftnerror import *
from bitparser import BitParser

class _message (BitParser):
    format = (
            ('msgVersion', 'uintle:16'),
            ('origNode', 'uintle:16'),
            ('destNode', 'uintle:16'),
            ('origNet', 'uintle:16'),
            ('destNet', 'uintle:16'),
            ('attributes', 'uintle:16'),
            ('cost', 'uintle:16'),
            ('dateTime', 'bits:160'),
            ('toUsername', 'cstring'),
            ('fromUsername', 'cstring'),
            ('subject', 'cstring'),
            ('body', 'cstring'),
            )

class Message (object):
    def readCString(self):
        x = self.bits.pos
        nul = self.bits[x:].find('0x00', bytealigned=True)[0]
        bytes = self.bits[x:x+nul].tobytes()
        self.bits.pos = x + nul + 8

        return bytes

    def parse(self, bits=None, fd=None):
        if bits is None:
            bits = bitstring.Bits(fd)

        self.fields = _message().parse(bits)
        self.bits = bits

