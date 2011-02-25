#!/usr/bin/python

import os

import fidonet
import fidonet.app
import fidonet.nodelist
from fidonet.nodelist import Node

class App (fidonet.app.App):

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-N', '--noroute', action='store_true')
        p.add_option('-z', '--zone', default='1')
        p.add_option('-I', '--internet', '--ina', action='store_true')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.cfg.get('fidonet', 'nodelist').split()[0]
            self.opts.nodelist = os.path.join(
                    os.path.dirname(nodelist), 'nodeindex.db')


        self.log.info('using nodelist %s' % self.opts.nodelist)
        fidonet.nodelist.setup('sqlite:///%s' % self.opts.nodelist)
        session = fidonet.nodelist.broker()

        for addr in args:
            dst = fidonet.Address(addr)
            print 'Finding route to', dst.ftn

            node = session.query(Node).filter(Node.address==dst.ftn).first()

            if self.opts.noroute:
                hub = None
                host = None
            else:
                hub = session.query(Node).filter(Node.net==dst.net).filter(Node.kw=='Hub').first()
                host = session.query(Node).filter(Node.net==dst.net).filter(Node.node==0).first()

            if hub is None and host is None and node:
                print dst.ftn, 'DIRECT'
            elif hub and (not self.opts.noroute or node and node.kw in ['Pvt', 'Hold']):
                print dst.ftn, 'HUB', fidonet.Address(hub.address).ftn
            elif host and (not self.opts.noroute or node and node.kw in ['Pvt', 'Hold']):
                print dst.ftn, 'HOST', fidonet.Address(host.address).ftn
            elif not node:
                print dst.ftn, 'ORPHAN'
            else:
                print dst.ftn, 'DIRECT'

if __name__ == '__main__':
    App.run()

