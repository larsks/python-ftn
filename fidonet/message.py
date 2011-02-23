import os
import sys
import bitstring

from ftnerror import *
from bitparser import Struct, Field, CString

Message = Struct(
            Field('msgVersion', 'uintle:16'),
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            Field('attributes', 'uintle:16'),
            Field('cost', 'uintle:16'),
            Field('dateTime', 'bytes:20'),
            CString('toUsername'),
            CString('fromUsername'),
            CString('subject'),
            CString('body'),
            )

