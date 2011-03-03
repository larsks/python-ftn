import os
import sys
import fnmatch
import logging

import fidonet
import fidonet.nodelist
from fidonet.nodelist import Node
from fidonet.ftnerror import *
from fidonet.util import commentedfilereader

class Router (object):
    '''Select routes for FTN addresses based on the nodelist and a routing
    policy file.

    Policy syntax
    =============

    Router() supports a subset of FrontDoor's routing commands::

      <route-spec> ::= <simple-route-command> <address-list>
                     | <targeted-to-command> <target-address> <address-list>

      <simple-route-command> ::= 'NO-ROUTE'
                               | 'DIRECT'
                               | 'HUB-ROUTE'
                               | 'HOST-ROUTE'

      <targeted-route-command> ::= 'ROUTE-TO'

      <address-list> ::= <address-or-flag>
                       | <address-or-flag> ' ' <address-list>

      <address-or-flag> ::= <address-spec> | <flag-spec>

      <address-spec> ::= '*'
                       | <digit> ':' '*'
                       | <digit> ':' <digit> '/' '*'
                       | <digit> ':' <digit> '/' <digit>

      <flag-spec> ::= '@' <flag-name> ':' <address-spec>

      <digit> :== [0-9]+

    DIRECT
    ------

    Route the packet directly to a node.

    HOST-ROUTE
    ----------

    Route packets to the network host.  This simply replaces the node
    number with ``0`` (so 1:322/761 would get routed to 1:322/0).

    HUB-ROUTE
    ---------

    Route packets to a network hub, if available, otherwise behaves like
    ``HOST-ROUTE``.

    NO-ROUTE
    --------

    Like ``DIRECT``, unless the node is marked ``Hold`` or ``Pvt`` in the
    node list, in which case it acts like ``HUB-ROUTE``.  This is the
    default behavior absent any other configuration.

    ROUTE-TO
    --------

    Route packets to the specified target node.

    Address matching
    ================

    The router uses glob-style matching for addresses.  This means that
    while you can do sane things like this::

      no-route 1:322/*

    You can also do silly things like this:

      no-route 1:3*

    The latter will apply the ``no-route`` policy to anything in a net that
    starts with ``3``.

    Flag matching
    =============

    You can limit address matches to nodes that are flying certain flags in
    the nodelist.  For example, if you want to apply the ``no-route``
    policy only to nodes capabile of accepting BinkD connections, you might
    do this::

      no-route @IBN:*

    You can combine flags and address patterns.  To apply the ``direct``
    policy to nodes in 1:322/* flying the ``IBN`` flag::

      direct @IBN:1:322/*

    API Examples
    ============

    Make the nodelist index available::

      >>> from fidonet.nodelist import Nodelist
      >>> nl = Nodelist('sqlite:///nl.d/nodelist.idx')
      >>> nl.setup()

    Create a new router::

      >>> router = Router(nl, 'route.cfg')

    Find the route to 1:322/761::

      >>> router['1:322/761']
      (1:322/761, ('no-route',))

    Find the route to 2:20/228::

      >>> router['2:20/228']
      (2:20/0, ('hub-route',))

    '''

    def __init__ (self,
            nodelist,
            route_file=None,
            default='no-route'):
        self.nodelist = nodelist
        self.routes = []
        self.default = self.parse_one_line('%s *' % default)

        if route_file is not None:
            self.read_route_file(route_file)

    def parse_one_line(self, line):
        cmd, args = line.split(None, 1)
        args = args.split()
        cmd = cmd.replace('-', '_').lower()

        if hasattr(self, 'cmd_%s' % cmd):
            return getattr(self, 'cmd_%s' % cmd)(args)
        else:
            raise InvalidRoute(line)

    def read_route_file (self, route_file):
        for line in commentedfilereader(open(route_file)):
            rspec = self.parse_one_line(line)
            self.routes.append(rspec)

    def cmd_route_to(self, args):
        target = fidonet.Address(args.pop(0))
        return (('route-to', target), args)

    def cmd_direct(self, args):
        return (('direct',), args)

    def cmd_no_route(self, args):
        return (('no-route',), args)

    def cmd_hub_route(self, args):
        return (('hub-route',), args)

    def cmd_host_route(self, args):
        return (('host-route',), args)

    def lookup_route(self, addr, node=None):
        route = self.default

        logging.debug('finding route for %s (default = %s)' % (addr,
            route))

        for rspec in self.routes:
            logging.debug('check %s against %s' % (addr, rspec))
            for pat in rspec[1]:
                if pat.startswith('@'):
                    flag, pat = pat[1:].split(':', 1)

                    if node is None:
                        continue
                    elif node and not flag in [x.flag_name for x in
                            node.flags]:
                        continue

                    logging.debug('flag match on %s for %s' % (flag, addr))
                if fnmatch.fnmatch(addr.ftn, pat):
                    logging.debug('matched %s, pat=%s' % (addr, pat))
                    route = rspec[0]

        return route

    def route(self, addr):
        addr = fidonet.Address(addr)
        session = self.nodelist.broker()
        
        node = session.query(Node).filter(Node.address==addr.ftn).first()
        logging.debug('found node = %s' % node)

        rspec = self.lookup_route(addr, node)

        hub = session.query(Node)\
                .filter(Node.zone==addr.zone)\
                .filter(Node.net==addr.net)\
                .filter(Node.kw=='Hub').first()
        host = session.query(Node)\
                .filter(Node.zone==addr.zone)\
                .filter(Node.net==addr.net)\
                .filter(Node.node=='0').first()

        logging.debug('found hub = %s' % hub)
        logging.debug('found host = %s' % host)

        action = rspec[0]
        if action == 'direct':
            return (addr, rspec)
        elif action == 'no-route':
            if node is None or node.kw in ['pvt', 'hold']:
                if hub:
                    return (fidonet.Address(hub.address), rspec)
                elif host:
                    return (fidonet.Address(host.address), rspec)
            else:
                return (fidonet.Address(node.address), rspec)
        elif action == 'route-to':
            return (fidonet.Address(rspec[1]), rspec)
        elif action == 'hub-route':
            if hub:
                return (fidonet.Address(hub.address), rspec)
            elif host:
                return (fidonet.Address(host.address), rspec)
        elif action == 'host-route':
            if host:
                return (fidonet.Address(host.address), rspec)

        return (None, None)

    def __getitem__ (self, addr):
        return self.route(addr)

