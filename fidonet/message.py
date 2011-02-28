'''A wrapper class for FTN format messages.

Reading a message
-----------------

Read a packet from a file using the ``fidonet.MessageFactory``
method:

    >>> import fidonet
    >>> msg = fidonet.MessageFactory(open('tests/sample.msg'))

Accessing message data
-----------------------

You can access message data as a dictionary:

    >>> msg['fromUsername']
    'Lars'

Or using dot notation:

    >>> msg.fromUsername
    'Lars'

Special properties
------------------

The ``origAddr`` and ``destAddr`` properties return the corresponding
address as a ``fidonet.Address`` instance:

    >>> msg.origAddr.ftn
    '322/761'

You can assign an Address object to this property to update the packet:

    >>> from fidonet.address import Address
    >>> msg.origAddr = Address('1:100/100')
    >>> msg.origAddr.ftn
    '1:100/100'

The ``body`` property returns a MessageBody instance:

    >>> b = msg.body
    >>> b.klines['MSGID:']
    ['1:322/761 ea6ec1dd']
    >>> b.area = 'FIDO_UTIL'
    >>> msg.body = b

Writing a message
-----------------

Write a message to an open file using the ``write`` method:

    >>> msg.write(open('updated.msg', 'w'))
'''

import os
import sys
import logging

from ftnerror import *
from util import *
from bitparser import Container
import odict
from formats import attributeword

class Message (Container):
    def _setAW (self, aw):
        self['attributeWord'] = attributeword.AttributeWordParser.build(aw)

    def _getAW (self):
        self['attributeWord'].pos = 0
        return attributeword.AttributeWordParser.parse(self['attributeWord'])

    attributeWord = property(_getAW, _setAW)

    def _getBody (self):
        return MessageBodyParser.parse(self['body'])

    def _setBody (self, body):
        self['body'] = MessageBodyParser.build(body)

    body = property(_getBody, _setBody)

    origAddr = ftn_address_property('orig')
    destAddr = ftn_address_property('dest')

    def __str__ (self):
        text = [
                'From: %(fromUsername)s @ %(origAddr)s' % self,
                'To: %(toUsername)s @ %(destAddr)s' % self,
                'Date: %(dateTime)s' % self,
                'Subject: %(subject)s' % self,
                ]
        flags = [ 'Flags:' ]
        for k,v in self.attributeWord.items():
            if v:
                flags.append(k.upper())

        text.append(' '.join(flags))
        return '\n'.join(text)

    def __build__ (self):
        body = self.body

        # unilaterally prefer point addressing in message metadata.
        # and always embed point addressing in message body
        # control lines.
        if self.get('origPoint', 0) > 0:
            body.klines['FMPT'] = [self.origPoint]
        if self.get('origPoint', 0) > 0:
            body.klines['TOPT'] = [self.destPoint]

        self.body = body

    def __parse__ (self):
        body = self.body

        if not 'origPoint' in self:
            if 'FMPT' in body.klines:
                self['origPoint'] = body.klines['FMPT'][0]
            else:
                self['origPoint'] = 0
        if not 'destPoint' in self:
            if 'TOPT' in body.klines:
                self['destPoint'] = body.klines['TOPT'][0]
            else:
                self['destPoint'] = 0

class MessageBody (Container):
    def __str__(self):
        return self.build()\
                .replace('\r', '\n')\
                .replace('\x01', '[K]')

# Everything below this is an ungodly mess.  Why, Fidonet, why!?

class _MessageBodyParser (object):
    kludgePrefix = '\x01'

    def create(self):
        body = MessageBody(self, {
            'area': None,
            'origin': None,
            'klines': odict.odict(),
            'seenby': [],
            'body': '',
            })

        body.__struct__ = self

        return body

    def parse(self, raw):
        msg = self.create()

        state = 0
        body = []

        for line in raw.split('\r'):
            #logging.debug('Got line [%d]: %s' % (state, line))
            if state == 0:
                state = 1

                if line.startswith('AREA:'):
                    msg['area'] = line.split(':', 1)[1]
                    continue

            if state == 1:
                if line.startswith('\x01'):
                    self.addKludge(msg, line)
                elif line.startswith(' * Origin:'):
                    msg['origin'] = line[11:]
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
                    raise InvalidMessage('Unexpected: %s'    % line)

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
            lines.append(' * Origin: %s' % msg['origin'])

        for seenby in msg['seenby']:
            lines.append('SEEN-BY: %s' % seenby)

        return '\r'.join(lines)

    def addKludge(self, msg, line):
        k,v = line[1:].split(None, 1)

        if k in msg['klines']:
            msg['klines'][k].append(v)
        else:
            msg['klines'][k] = [v]

MessageBodyParser = _MessageBodyParser()

