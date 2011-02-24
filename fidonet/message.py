import os
import sys
import bitstring
from StringIO import StringIO

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

class MessageBody (object):
    def __init__ (self, raw, kludgePrefix=None):
        self.area = None
        self.origin = None
        self.klines = []
        self.kdict = {}
        self.seenby = []
        self.body = None
        self.raw = raw

        if kludgePrefix is not None:
            self.kprefix = kludgePrefix
        else:
            self.kprefix = '\x01'

        self.parseLines()

    def addKludge(self, line):
        k,v = line.split(None, 1)
        k = k[1:]

        if self.kdict.has_key(k):
            self.kdict[k].append(v)
        else:
            self.kdict[k] = [v]
            self.klines.append(k)

    def parseLines(self):

        state = 0
        body = []

        for line in self.raw.split('\r'):
            print 'STATE:', state
            if state == 0:
                state = 1

                if line.startswith('AREA:'):
                    self.area = line.split(':', 1)[1]
            elif state == 1:
                if line.startswith('\x01'):
                    self.addKludge(line)
                elif line.startswith(' * Origin:'):
                    self.origin = line
                    state = 2
                else:
                    body.append(line)
            elif state == 2:
                if line.startswith('\x01'):
                    self.addKludge(line)
                elif line.startswith('SEEN-BY:'):
                    self.seenby.append(line)
                elif len(line) == 0:
                    pass
                else:
                    raise ValueError('Unexpected: %s'    % line)

        self.body = '\r\n'.join(body)

    def __str__ (self):
        return '\n'.join(self.lines)

def MessageFactory(bits=None, fd=None):
    if bits is None:
        bits = bitstring.ConstBitStream(fd)

    msg = fts0001.parse(bits, Message)
    return msg

if __name__ == '__main__':
    m = MessageFactory(fd=open(sys.argv[1]))

