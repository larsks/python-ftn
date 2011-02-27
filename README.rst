====================
FTN Tools for Python
====================

``Python-ftn`` is an API and suite of tools for manipulating FTN message and
packet data.  The package currently includes tools for:

- Generating FTN messages.  
- Editing message data.  
- Displaying and querying message data.  
- Packing/unpacking FTN mail packets.  
- Editing packet data.  
- Displaying and querying packet data.  
- Parsing and querying FTN nodelists.  
- Making routing decsisions from nodelist data.

The ``python-ftn`` API makes it easy to develop new tools that interact with
FTN format data.

Python-ftn support FTS-0001 "on disk" and "packed" messages (and can
convert between them), and supports both FTS-0001 ("type 2") and FSC-0048
("type 2+") packets.

Requirements
============

This software requires the following Python modules:

- `bitstring`_ -- for reading/writing binary formats.
- sqlite3 -- for interacting with SQLite databases.

.. _bitstring: http://code.google.com/p/python-bitstring/

Installation
============

::

  python setup.py install

Author
======

Python-ftn was written by Lars Kellogg-Stedman, ``lars@oddbit.com`` or
Lars @ 1:322/761.

License
=======

Python-ftn is free software: you can redistribute it and/or modify it under
the terms of the `GNU General Public License`_ as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along
with this software. If not, see <http://www.gnu.org/licenses/>.

Fido, FidoNet and the dog-with-diskette are registered trademarks of Tom
Jennings, San Francisco California, USA.

.. _gnu general public license:
   http://www.gnu.org/licenses/gpl-3.0-standalone.html

