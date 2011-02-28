'''This is the on-disk message format described in FTS-0001_.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import *
from fidonet.message import Message

MessageParser = Struct('message',
        PaddedString('fromUsername', 36, '\x00'),
        PaddedString('toUsername', 36, '\x00'),
        PaddedString('subject', 72, '\x00'),
        PaddedString('dateTime', 20, '\x00'),
        Field('timesRead', 'uintle:16'),
        Field('destNode', 'uintle:16'),
        Field('origNode', 'uintle:16'),
        Field('cost', 'uintle:16'),
        Field('destNet', 'uintle:16'),
        Field('origNet', 'uintle:16'),
        Field('destZone', 'uintle:16'),
        Field('origZone', 'uintle:16'),
        Field('destPoint', 'uintle:16'),
        Field('origPoint', 'uintle:16'),
        Field('replyTo', 'uintle:16'),
        BitStream('attributeWord', 16),
        Field('nextReply', 'uintle:16'),
        CString('body', default=''),

        factory=Message
        )

