import os
import sys
import tempfile
import glob
import errno

import fidonet
import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag
from fidonet.router import Router

class App(fidonet.app.AppUsingFiles):
    logtag = 'fidonet.pftransport'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-r', '--routes')
        p.add_option('-T', '--transport', default='ifmail')
        p.add_option('-q', '--quiet', action='store_true')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist
            self.log.debug('using nodelist = %s' % self.opts.nodelist)

        if self.opts.routes is None:
            self.opts.routes = self.get_cfg_path(
                    'fidonet', 'routes')

        self.log.info('using nodelist %s' % self.opts.nodelist)
        if self.opts.routes:
            self.log.info('using routes from %s' % self.opts.routes)

        nl = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nl.setup()
        session = nl.broker()

        router = Router(nl, self.opts.routes)

        nodes = session.query(Node).join('flags')

        if self.opts.output:
            sys.stdout = open(self.opts.output, 'w')

        for node in nodes:
            addr = fidonet.Address(node.address)
            rspec = router[addr]

            if not self.opts.quiet:
                print '# %s -> %s [%s]' % (addr, rspec[0], ' '.join([str(x)
                    for x in rspec[1]]))
            print '%s\t%s:%s' % (addr.rfc, self.opts.transport,
                    rspec[0].rfc)

if __name__ == '__main__':
    App.run()

