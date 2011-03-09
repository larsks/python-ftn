import os

import fidonet
import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag

class App(fidonet.app.App):
    logtag = 'fidonet.binknodes'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-D', '--domain',
                default='fidonet')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist

        nl = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nl.setup()
        session = nl.broker()

        nodes = session.query(Node).join('flags').filter(
                Flag.flag_name == 'IBN')

        for n in nodes:
            inet = n.inet('IBN')
            if inet is None:
                continue

            print 'Node %-20s %s' % (
                    ('%s@%s' % (n.address, self.opts.domain)),
                    inet
                    )

if __name__ == '__main__':
    App.run()

