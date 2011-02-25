'''This parses the attributeWord data field from FTS-0001_, present in both
packed and on-disk messages.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import Struct, Field, CString, BitStream

AttributeWordParser = Struct(
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

