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

Writing a message
-----------------

Write a message to an open file using the ``write`` method:

    >>> msg.write(open('updated.msg', 'w'))
'''

import os
import sys
import logging

import fidonet
from ftnerror import *
from util import *
from bitparser import Container
import odict
from formats import attributeword

class Message (Container):
    origAddr = ftn_address_property('orig')
    destAddr = ftn_address_property('dest')

    def __init__ (self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self['parsed_body'] = MessageBodyParser.create()

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

        if self.parsed_body.area:
            text.append('Area: %(area)s' % self.parsed_body)

        return '\n'.join(text)

    def __pack__ (self):
        # unilaterally prefer point addressing in message metadata.
        # and always embed point addressing in message body
        # control lines.
        if self.get('origPoint', 0) > 0:
            self.parsed_body.klines['FMPT'] = [self.origPoint]
        if self.get('destPoint', 0) > 0:
            self.parsed_body.klines['TOPT'] = [self.destPoint]

        # Add INTL control line using origin and destination.
        # (NOT for echomail)
        if self.parsed_body.area is None:
            self.parsed_body.klines['INTL'] = ['%s %s' % (
                self.destAddr.pointless,
                self.origAddr.pointless)]

        self['body'] = self.parsed_body.pack()

    def __unpack__ (self):
        logging.debug('parsing a message')

        self['parsed_body'] = MessageBodyParser.unpack(self['body'])

        if 'INTL' in self.parsed_body.klines:
            intlDest, intlOrig = self.parsed_body.klines['INTL'][0].split()
            self.destAddr = fidonet.Address(intlDest)
            self.origAddr = fidonet.Address(intlOrig)

        # Make sure we have origZone/destZone keys, because we need these
        # for a diskmessage (and for various sorts of address manipulation)
        if not 'origZone' in self:
            self['origZone'] = 0
        if not 'destZone' in self:
            self['destZone'] = 0

        # Extract point information from control lines.
        if self.get('origPoint', 0) == 0:
            logging.debug('looking for FMPT')
            if 'FMPT' in self.parsed_body.klines:
                self['origPoint'] = self.parsed_body.klines['FMPT'][0]
                logging.debug('set origPoint = %(origPoint)s' % self)
            else:
                self['origPoint'] = 0
        if self.get('destPoint', 0) == 0:
            logging.debug('looking for TOPT')
            if 'TOPT' in self.parsed_body.klines:
                self['destPoint'] = self.parsed_body.klines['TOPT'][0]
                logging.debug('set destPoint = %(destPoint)s' % self)
            else:
                self['destPoint'] = 0

class MessageBody (Container):
    def __str__(self):
        return self.pack()\
                .replace('\r', '\n')\
                .replace('\x01', '[K]')

    def add_kludge(self, k, v):
        if k in self.klines:
            self.klines[k].append(v)
        else:
            self.klines[k] = [v]

# Everything below this is an ungodly mess.  Why, Fidonet, why!?

class _MessageBodyParser (object):
    kludgePrefix = '\x01'

    def create(self):
        body = MessageBody(self, {
            'area': None,
            'origin': None,
            'klines': odict.odict(),
            'seenby': [],
            'text': '',
            'body': '',
            })

        body.__struct__ = self

        return body

    def unpack(self, raw):
        msg = self.create()

        state = 0
        text = []

        for line in raw.split('\r'):
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
                    text.append(line)
            elif state == 2:
                if line.startswith('\x01'):
                    self.addKludge(msg, line)
                elif line.startswith('SEEN-BY:'):
                    msg['seenby'].append(line.split(': ', 1)[1])
                elif len(line) == 0:
                    pass
                else:
                    raise InvalidMessage('Unexpected: %s'    % line)

        msg['text'] = '\n'.join(text)

        return msg

    def pack(self, msg):
        lines = []

        if msg['area']:
            lines.append('AREA:%(area)s' % msg)

        for k,vv in msg['klines'].items():
            for v in vv:
                lines.append('%s%s %s' % (self.kludgePrefix, k,v))

        lines.extend(msg['text'].split('\n'))

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

