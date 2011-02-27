============================================================
Pytnon-FTN: API and tools for Fidonet and other FTN networks
============================================================

I have put together a suite of tools for manipulating FTN message and
packet data.  The package currently includes tools for:

- Generating FTN messages.
- Editing message data.
- Displaying and querying message data.
- Packing/unpacking FTN mail packets.
- Editing packet data.
- Displaying and querying packet data.
- Parsing and querying FTN nodelists.
- Making routing decsisions from nodelist data.

The python-ftn API makes it easy to develop new tools that interact
with FTN format data.

Python-ftn support FTS-0001 "on disk" and "packed" messages (and can
convert between them), and supports both FTS-0001 ("type 2") and
FSC-0048 ("type 2+") packets.

Availability
============

Python-ftn is available from:

- http://projects.oddbit.com/python-ftn

Online documentation is available from:

- https://github.com/larsks/python-ftn/wiki

Examples
========

Change the destination of an outbound packet::

  $ ftn-editpkt --dest 1:322/761 00000001.pkt

Change the sender name in a message::

  $ ftn-editmsg --from 'A Different Person' 1.msg

Create and pack a message for delivery::

  $ echo "My body text" |
  ftn-makemsg \
    --from 'Lars Kellogg-Stedman' \
  --to 'Someone Else' \
  --orig 1:322/761 \
  --dest 99:99/99 \
  --subject "This is a test" \
  --flag killSent --flag private |
  ftn-pack -d 1:322/759 --out 014202f7.out

Examine the generated packet::

  $ ftn-scanpkt 014202f7.out  -m
  ======================================================================
  014202f7.out:  1:322/761 -> 1:322/759 @ 2011-02-26 23:31:59
  ======================================================================

  [000]
  From: Lars Kellogg-Stedman @ 322/761
  To: Someone Else @ 99/99
  Date: 26 Feb 11  23:31:59
  Subject: This is a test
  Flags: KILLSENT PRIVATE
 
Author
======

Python-ftn was written by Lars Kellogg-Stedman.

- Fidonet: Lars @ 1:322/761
- Internet: lars@oddbit.com

