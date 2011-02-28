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

    Examples
    ========

    Make the nodelist index available::

      >>> from fidonet import nodelist
      >>> nodelist.setup_nodelist('sqlite:///tests/nodeindex.db')

    Create a new router::

      >>> router = Router('tests/route.cfg')

    Find the route to 1:322/761::

      >>> router['1:322/761']
      (1:322/0, ('no-route',))

    Find the route to 2:20/228::

      >>> router['2:20/228']
      (2:20/0, ('hub-route',))

    '''

    def __init__ (self,
            route_file='route.cfg',
            default='no-route'):
        self.routes = []
        self.default = self.parse_one_line('%s *' % default)
        self.read_route_file(route_file)

    def parse_one_line(self, line):
        cmd, args = line.split(None, 1)
        args = args.split()
        cmd = cmd.replace('-', '_')

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

        for rspec in self.routes:
            for pat in rspec[1]:
                if pat.startswith('@'):
                    flag, pat = pat[1:].split(':', 1)
                    if node and not flag in [x.flag_name for x in
                            node.flags]:
                        continue
                if fnmatch.fnmatch(addr.ftn, pat):
                    route = rspec[0]

        return route

    def route(self, addr):
        addr = fidonet.Address(addr)
        session = fidonet.nodelist.broker()
        
        node = session.query(Node).filter(Node.address==addr.ftn).first()

        rspec = self.lookup_route(addr, node)

        hub = session.query(Node).filter(Node.net==addr.net).filter(Node.kw=='Hub').first()
        host = session.query(Node).filter(Node.net==addr.net).filter(Node.node==0).first()

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

if __name__ == '__main__':
    args = sys.argv[1:]

    fidonet.nodelist.setup_nodelist('sqlite:///%s' % args.pop(0))
    router = Router(args.pop(0))

    for addr in args:
        route = router[addr]
        print '%s via %s (using policy %s)' % (
                addr, route[0], route[1])

