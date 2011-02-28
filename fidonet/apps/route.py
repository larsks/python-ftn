#!/usr/bin/python

import os

import fidonet
import fidonet.app
import fidonet.nodelist
import fidonet.router
from fidonet.nodelist import Node

class App (fidonet.app.App):

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-r', '--routes')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.cfg.get('fidonet', 'nodelist').split()[0]
            self.opts.nodelist = os.path.join(
                    os.path.dirname(nodelist), 'nodeindex.db')
        if self.opts.routes is None:
            self.opts.routes = self.cfg.get('fidonet', 'routes')

        self.log.info('using nodelist %s' % self.opts.nodelist)
        self.log.info('using routes from %s' % self.opts.routes)

        router = fidonet.router.Router(self.opts.routes)

        fidonet.nodelist.setup_nodelist('sqlite:///%s' % self.opts.nodelist)
        session = fidonet.nodelist.broker()

        for addr in args:
            addr = fidonet.Address(addr)
            rspec = router[addr]
            print addr, 'via', rspec[0], 'using', ' '.join([str(x) for x in
                rspec[1]])

if __name__ == '__main__':
    App.run()

