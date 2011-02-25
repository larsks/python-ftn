'''This is the on-disk message format described in FTS-0001_.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import Struct, Field, CString, BitStream

MessageParser = Struct(
            Field('fromUsername', 'bytes:36', default='',
                utransform=lambda x: x.rstrip('\x00')),
            Field('toUsername', 'bytes:36', default='',
                utransform=lambda x: x.rstrip('\x00')),
            Field('subject', 'bytes:72', default='',
                utransform=lambda x: x.rstrip('\x00')),
            Field('dateTime', 'bytes:20',
                default=' '*20,
                utransform=lambda x: x.rstrip('\x00'),
                ptransform=lambda x: (x + ' '*20)[:20]),
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
            BitStream('attributeWord', length=16),
            Field('nextReply', 'uintle:16'),
            CString('body', default=''),
        )

