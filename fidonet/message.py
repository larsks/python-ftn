import os
import sys
import bitstring
from StringIO import StringIO

from ftnerror import *
from util import *
from bitparser import Struct, Field, CString, Container

import odict

attributeWordParser = Struct(
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

class Message (Container):
    def _setAW (self, aw):
        self['attributeWord'] = attributeWordParser.build(aw)

    def _getAW (self):
        self['attributeWord'].pos = 0
        return attributeWordParser.parse(self['attributeWord'])

    attributeWord = property(_getAW, _setAW)

    def _getBody (self):
        return MessageBodyParser.parse(self['body'])

    def _setBody (self, body):
        self['body'] = MessageBodyParser.build(body)

    body = property(_getBody, _setBody)

    origAddr = ftn_address_property('orig')
    destAddr = ftn_address_property('dest')

MessageParser = Struct(
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

            factory = Message
            )

class MessageBody (Container):
    def render(self):
        return MessageBodyParser.build(self)\
                .replace('\r', '\n')\
                .replace('\x01', '[K]')

class _MessageBodyParser (object):
    def __init__ (self, kludgePrefix='\x01'):
        self.kludgePrefix = kludgePrefix

    def parse(self, raw):
        msg = MessageBody({
            'area': None,
            'origin': None,
            'klines': odict.odict(),
            'seenby': [],
            'body': [],
            })

        state = 0
        body = []

        for line in raw.split('\r'):
            if state == 0:
                state = 1

                if line.startswith('AREA:'):
                    msg['area'] = line.split(':', 1)[1]
            elif state == 1:
                if line.startswith('\x01'):
                    self.addKludge(msg, line)
                elif line.startswith(' * Origin:'):
                    msg['origin'] = line
                    state = 2
                else:
                    body.append(line)
            elif state == 2:
                if line.startswith('\x01'):
                    self.addKludge(msg, line)
                elif line.startswith('SEEN-BY:'):
                    msg['seenby'].append(line.split(': ', 1)[1])
                elif len(line) == 0:
                    pass
                else:
                    raise ValueError('Unexpected: %s'    % line)

        msg['body'] = '\n'.join(body)

        return msg

    def build(self, msg):
        lines = []

        if msg['area']:
            lines.append('AREA:%(area)s' % msg)

        for k,vv in msg['klines'].items():
            for v in vv:
                lines.append('%s%s %s' % (self.kludgePrefix, k,v))

        lines.extend(msg['body'].split('\n'))

        if msg['origin']:
            lines.append(msg['origin'])

        for seenby in msg['seenby']:
            lines.append('SEEN-BY: %s' % seenby)

        return '\r'.join(lines)

    def addKludge(self, msg, line):
        k,v = line[1:].split(None, 1)

        if k in msg['klines']:
            msg['klines'][k].append(v)
        else:
            msg['klines'][k] = [v]

    def __str__ (self):
        return '\n'.join(self.lines)

MessageBodyParser = _MessageBodyParser()

def MessageFactory(bits=None, fd=None):
    if bits is not None:
        return MessageParser.parse(bits)
    elif fd is not None:
        return MessageParser.parse_fd(fd)

if __name__ == '__main__':
    m = MessageFactory(fd=open(sys.argv[1]))

