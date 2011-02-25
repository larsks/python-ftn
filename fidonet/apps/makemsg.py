#!/usr/bin/python

import sys

from fidonet import Address
from fidonet.formats import *
import fidonet.app

class App (fidonet.app.App):
    logtag = 'fidonet.makemsg'

    def create_parser(self):
        p = super(App, self).create_parser()

        p.add_option('-k', '--kludge', action='append', default=[])
        p.add_option('-s', '--subject')
        p.add_option('-f', '--fromuser', '--from')
        p.add_option('-t', '--touser', '--to')
        p.add_option('-o', '--origin', '--orig')
        p.add_option('-d', '--destination', '--dest')
        p.add_option('--output', '--out')
        p.add_option('--disk', action='store_false',
                dest='packed')
        p.add_option('--packed', action='store_true',
                dest='packed')

        p.set_default('packed', True)

        return p

    def handle_args (self, args):
        if self.opts.packed:
            msg = packedmessage.MessageParser.create()
        else:
            msg = diskmessage.MessageParser.create()

        if not self.opts.origin:
            try:
                self.opts.origin = self.cfg.get('fidonet', 'address')
                self.log.debug('got origin address = %s' % self.opts.origin)
            except:
                pass

        if self.opts.fromuser:
            msg.fromUsername = self.opts.fromuser
            self.log.debug('set fromUsername = %s' % msg.fromUsername)
        if self.opts.touser:
            msg.toUsername = self.opts.touser
            self.log.debug('set toUsername = %s' % msg.toUsername)
        if self.opts.subject:
            msg.subject = self.opts.subject
            self.log.debug('set subject = %s' % msg.subject)

        if self.opts.origin:
            msg.origAddr = Address(self.opts.origin)
            self.log.debug('set originAddr = %s' % msg.origAddr)
        if self.opts.destination:
            msg.destAddr = Address(self.opts.destination)
            self.log.debug('set destinAddr = %s' % msg.destAddr)

        body = msg.body

        for k in self.opts.kludge:
            k_name, k_val = k.split(' ', 1)
            body.klines[k_name] = body.klines.get(k_name, []) + [k_val]

        if args:
            sys.stdin = open(args[0])
        if self.opts.output:
            sys.stdout = open(self.opts.output, 'w')

        body.body = sys.stdin.read()
        msg.body = body

        msg.write(sys.stdout)

if __name__ == '__main__':
    App.run()

