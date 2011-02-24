import os
import sys
import bitstring

from ftnerror import *
from bitparser import Struct, Field, CString

attributeWord = Struct(
        Field('private', 'uint:1'),
        Field('crash', 'uint:1'),
        Field('received', 'uint:1'),
        Field('sent', 'uint:1'),
        Field('fileAttached', 'uint:1'),
        Field('inTransit', 'uint:1'),
        Field('orphan', 'uint:1'),
        Field('killSent', 'uint:1'),
        Field('local', 'uint:1'),
        Field('holdForPickup', 'uint:1'),
        Field('unused1', 'uint:1'),
        Field('fileRequest', 'uint:1'),
        Field('returnReceiptRequested', 'uint:1'),
        Field('isReturnReceipt', 'uint:1'),
        Field('auditRequest', 'uint:1'),
        Field('fileUpdateRequest', 'uint:1'),
        )

fts0001 = Struct(
            Field('msgVersion', 'uintle:16'),
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            Field('attributeWord', 'bits:16'),
            Field('cost', 'uintle:16'),
            Field('dateTime', 'bytes:20'),
            CString('toUsername'),
            CString('fromUsername'),
            CString('subject'),
            CString('body'),
            )

class Message (dict):
    def __getattr__ (self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    def _setAW (self, aw):
        self['attributeWord'] = attributeWord.build(aw)

    def _getAW (self):
        self['attributeWord'].pos = 0
        return attributeWord.parse(self['attributeWord'])

    attributeWord = property(_getAW, _setAW)

def MessageFactory(bits=None, fd=None):
    if bits is None:
        bits = bitstring.ConstBitStream(fd)

    msg = fts0001.parse(bits, Message)
    return msg

if __name__ == '__main__':
    m = MessageFactory(fd=open(sys.argv[1]))

