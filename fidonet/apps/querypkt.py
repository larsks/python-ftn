#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app

class App (fidonet.app.App):
    logtag = 'fidonet.querypkt'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-q', '--query', action='append', default=[])
        p.add_option('--queryformat', '--qf')
        return p

    def query_pkt(self, src, name, ctx):
        pkt = fidonet.PacketFactory(src)
        
        try:
            if self.opts.queryformat:
                print self.opts.queryformat % pkt
            else:
                for k in self.opts.query:
                    print pkt[k]
        except KeyError, detail:
            print >>sys.stderr, 'error: %s: no such field.' % detail

    def handle_args(self, args):
        self.for_each_arg(self.query_pkt, args)

if __name__ == '__main__':
    App.run()

