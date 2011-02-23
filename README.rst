====================
FTN Tools for Python
====================

Example scripts
---------------

ftn-reroute
~~~~~~~~~~~

``ftn-reroute`` changes the destination address in a packet.  You need to
either provide an output file using the ``-o`` option or specify ``-i`` if
you want to modify the packet in place::

  ftn-reroute -r 1:123/500 05E6F017.PKT

ftn-unpack
~~~~~~~~~~

``ftn-unpack`` unpacks messages from a packet and places them in an output
directory::

  ftn-unpack -o msgdir 05E6F017.PKT

ftn-pack
~~~~~~~~

``ftn-pack`` creates a message packet from a list of messages. For example,
if we have a directory called ``msgdir`` containing a number of messages
ready for delivery, we can run the following command::

  ftn-pack --to 1:322/759 --from 1:322/761 msgdir/*.msg

This will create a file called "014202f7.out" in the current directory.

