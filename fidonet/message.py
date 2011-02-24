import os
import sys
import bitstring
from StringIO import StringIO

from ftnerror import *
from util import *
from bitparser import Struct, Field, CString, Container

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

class _MessageBodyParser (dict):
    def __init__ (self, kludgePrefix='\x01'):
        self.kludgePrefix = kludgePrefix

    def parse(self, raw):
        msg = Container({
            'area': None,
            'origin': None,
            'klines': ([], {}),
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

    def build(self, parsed):
        '''Rebuilds the message as:

                AREA:...
                Kludge lines
                Body
                Origin
                SEEN-BY'''

        msg = []

        if parsed['area']:
            msg.append('AREA:%(area)s' % parsed)

        for k in parsed['klines'][0]:
            for v in parsed['klines'][1][k]:
                msg.append('%s%s %s' % (self.kludgePrefix, k,v))

        msg.extend(parsed['body'].split('\n'))

        if parsed['origin']:
            msg.append(parsed['origin'])

        for seenby in parsed['seenby']:
            msg.append('SEEN-BY: %s' % seenby)

        return '\r'.join(msg)

    def addKludge(self, msg, line):
        k,v = line[1:].split(None, 1)

        if k in msg['klines'][0]:
            msg['klines'][1][k].append(v)
        else:
            msg['klines'][0].append(k)
            msg['klines'][1][k] = [v]

    def __str__ (self):
        return '\n'.join(self.lines)

MessageBodyParser = _MessageBodyParser()

def MessageFactory(bits=None, fd=None):
    if bits:
        return MessageParser.parse(bits)
    elif fd:
        return MessageParser.parse_fd(fd)

if __name__ == '__main__':
    m = MessageFactory(fd=open(sys.argv[1]))

