====================
FTN Tools for Python
====================

.. contents::

Parsing
=======

Parsing packets
---------------

::

  pkt = fidonet.PacketFactory(open('05E89CD6.PKT'))

  print 'FROM:', pkt.origAddr
  print '  TO:', pkt.destAddr

Parsing messages in a packet
----------------------------

::

  while True:
    try:
      msg = fidonet.MessageFactory(pkt.messages)
      print 'FROM: %s @ %s' % (msg.fromUsername, msg.origAddr)
      print '  TO: %s @ %s' % (msg.toUsername, msg.destAddr)
    except ftn.EndOfData:
      break

Modifying
=========

Modifying packet data
---------------------
 
::

  pkt.destAddr = fidonet.Address('1:123/500')
  pkt.time = time.localtime()

Modifying message data
----------------------

::

  msg.toUsername = 'Joe User'
  msg.destAddr = fidonet.Address('1:123/500')

  body = msg.body
  body.origin = ' * The Odd Bit (1:322/761)'
  body.seenby.append('1:322/761')
  
  msg.body = body

Creating
========

Creating messages
-----------------

::

  from fidonet.formats import *

  msg = packedmessage.MessageParser.create()

  msg.fromUsername = 'Lars'
  msg.toUsername = 'Joe'
  msg.subject = 'This is a test'

  msg.origAddr = fidonet.Address('1:322/761')
  msg.destAddr = fidonet.Address('1:322/759')

  # Add a body.
  b = msg.body
  b.body = '''this is a test.
  this is only a test.'''
  b.klines['INTL'] = ['1:322/761 1:322/759']
  msg.body = b

  # Set some attributes.
  attr = fidonet.message.attributeWordParser.create()
  attr.private = 1
  attr.killSent = 1
  msg.attributeWord = attr

Creating packets
----------------

::

  from fidonet.formats import *

  pkt = fsc0048packet.PacketParser.create()
  pkt.origAddr = fidonet.Address('1:322/761')
  pkt.destAddr = fidonet.Address('1:322/759')
  pkt.time = time.localtime()

  # add the message created in the previous example
  pkt.messages.append(msg.build())

Writing
=======

Writing messages
----------------

Writing a message in its native format::

  fd = open('1.msg', 'w')
  msg.write(fd)

Writing using an explicit format::

  from fidonet.formats import *
  diskmessage.MessageParser.write(msg, open('1.msg', 'w'))
  packedmessage.MessageParser.write(msg, open('2.msg', 'w'))

Writing packets
---------------

::

  fd = open('1.msg', 'w')
  pkt.write(fd)

Example scripts
===============

ftn-reroute
-----------

``ftn-reroute`` changes the destination address in a packet.  You need to
either provide an output file using the ``-o`` option or specify ``-i`` if
you want to modify the packet in place::

  ftn-reroute -r 1:123/500 05E6F017.PKT

ftn-unpack
----------

``ftn-unpack`` unpacks messages from a packet and places them in an output
directory::

  ftn-unpack -o msgdir 05E6F017.PKT

ftn-pack
--------

``ftn-pack`` creates a message packet from a list of messages. For example,
if we have a directory called ``msgdir`` containing a number of messages
ready for delivery, we can run the following command::

  ftn-pack --to 1:322/759 --from 1:322/761 msgdir/*.msg

This will create a file called "014202f7.out" in the current directory.

ftn-msgedit
-----------

``ftn-msgedit`` edits the information in a message header::

  ftn-msgedit --to 'Lars Kellogg-Stedman' --origin '1:123/500' msgdir/1.msg

Note that ``ftn-msgedit`` makes changes in place.

Fidonet Technical Standards
===========================

This software attempts to adhere to the following documents:

- FTS-0001.16_

  This describes the original Fidonet type 2 packet format and the packed
  message format.

- FSC-0048.02_

  This describes the type 2+ message packet.

- FTS-5000.02_

  This describes the format of the distribution nodelist.

.. _FTS-0001.16: http://www.ftsc.org/docs/fts-0001.016
.. _FSC-0048.02: http://www.ftsc.org/docs/fsc-0048.002
.. _FTS-5000.02: http://www.ftsc.org/docs/fts-5000.002

Message attributes
------------------

Because I had a hard time finding this information, here's the meaning of
the various message attributes:

private
  Message is private.
crash
  Message is to be sent immediately to recipient.
received
  Message has been received by the recipient.
sent
  Message was exported.
fileAttached
  A file is being sent along with the message.
inTransit
  The message is not for the local system and will be
  forwarded on to the final destination.
orphan
  The tosser does not know to where to route this mail.
killSent
  Delete this message after export.
local
  Message was created on this system.
holdForPickup
  Remote system must call for pickup.
fileRequest
  Message is a file request.
returnReceiptRequested
  The receipient is to send a return receipt to the sender.
isReturnReceipt
  This message is a return receipt.
auditRequest
  Every routing system is requested to send a return receipt.
fileUpdateRequest
  (unknown)

