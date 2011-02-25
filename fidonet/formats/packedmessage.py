'''This is the packed message format described in FTS-0001_.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import *
from fidonet.message import Message

MessageParser = Struct(
            Field('msgVersion', 'uintle:16', default=2),
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            BitStream('attributeWord', length=16),
            Field('cost', 'uintle:16'),
            PaddedString('dateTime', 20, ' '),
            CString('toUsername'),
            CString('fromUsername'),
            CString('subject'),
            CString('body', default=''),

            factory=Message
            )

