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
    def __init__ (self,
            route_file='route.cfg',
            default='direct'):
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

    def lookup_route(self, addr):
        route = self.default

        for rspec in self.routes:
            for pat in rspec[1]:
                if fnmatch.fnmatch(addr.ftn, pat):
                    route = rspec[0]

        return route

    def route(self, addr):
        addr = fidonet.Address(addr)
        rspec = self.lookup_route(addr)
        session = fidonet.nodelist.broker()
        
        node = session.query(Node).filter(Node.address==addr.ftn).first()
        hub = session.query(Node).filter(Node.net==addr.net).filter(Node.kw=='Hub').first()
        host = session.query(Node).filter(Node.net==addr.net).filter(Node.node==0).first()

        action = rspec[0]
        if action == 'direct':
            return (addr, rspec)
        elif action == 'no-route':
            if node is None or node['kw'] in ['pvt', 'hold']:
                if hub:
                    return (fidonet.Address(hub.address), rspec)
                elif host:
                    return (fidonet.Address(host.address), rspec)
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
    fidonet.nodelist.setup_nodelist('sqlite:///nodelist/nodeindex.db')

    args = sys.argv[1:]
    router = Router(args.pop(0))

    for addr in args:
        route = router[addr]
        print addr, route

