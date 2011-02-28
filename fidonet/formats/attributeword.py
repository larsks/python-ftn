'''This parses the attributeWord data field from FTS-0001_, present in both
packed and on-disk messages.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import *

AttributeWordParser = Struct('attributeWord',
        Boolean('private'),
        Boolean('crash'),
        Boolean('received'),
        Boolean('sent'),
        Boolean('fileAttached'),
        Boolean('inTransit'),
        Boolean('orphan'),
        Boolean('killSent'),
        Boolean('local'),
        Boolean('holdForPickup'),
        Boolean('unused1'),
        Boolean('fileRequest'),
        Boolean('returnReceiptRequested'),
        Boolean('isReturnReceipt'),
        Boolean('auditRequest'),
        Boolean('fileUpdateRequest'),
        )

