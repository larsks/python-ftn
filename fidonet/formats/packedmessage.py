'''This is the packed message format described in FTS-0001_.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import *
from fidonet.message import Message
from fidonet.formats import attributeword

MessageParser = Struct('message',
            Constant('msgVersion', 'uintle:16', 2),
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            attributeword.AttributeWordParser,
            Field('cost', 'uintle:16'),
            PaddedString('dateTime', 20, '\x00'),
            CString('toUsername'),
            CString('fromUsername'),
            CString('subject'),
            CString('body', default=''),

            factory=Message,
            )

