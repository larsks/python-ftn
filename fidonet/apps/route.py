#!/usr/bin/python

import os

import fidonet
import fidonet.app
from fidonet.router import Router
from fidonet.nodelist import Node, Nodelist

class App (fidonet.app.App):

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-r', '--routes')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            self.opts.nodelist = '%s.idx' % self.get_data_paths(
                    'fidonet', 'nodelist').next()
        if self.opts.routes is None:
            self.opts.routes = self.get_cfg_path(
                    'fidonet', 'routes')

        self.log.info('using nodelist %s' % self.opts.nodelist)

        if self.opts.routes:
            self.log.info('using routes from %s' % self.opts.routes)

        nl = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nl.setup()
        router = Router(nl, self.opts.routes)

        for addr in args:
            addr = fidonet.Address(addr)
            rspec = router[addr]
            print addr, 'via', rspec[0], 'using', rspec[1]

if __name__ == '__main__':
    App.run()

