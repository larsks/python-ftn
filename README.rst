====================
FTN Tools for Python
====================

.. contents::

Fidonet Technical Standards
===========================

This software attempts to adhere to the following documents:

- FTS-0001.16_

  This describes the original Fidonet packet format and the 
  packed message format.

- FSC-0048.02_

  This describes the type 2+ message packet.

.. _FTS-0001.16: http://www.ftsc.org/docs/fts-0001.016
.. _FSC-0048.02: http://www.ftsc.org/docs/fsc-0048.002

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

