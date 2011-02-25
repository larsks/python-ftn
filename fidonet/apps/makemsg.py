#!/usr/bin/python

import sys

import fidonet.app
from fidonet.message import MessageParser
from fidonet.address import Address

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

        return p

    def handle_args (self, args):
        msg = fidonet.message.MessageParser.create()

        if self.opts.fromuser:
            msg.fromUsername = self.opts.fromuser
        if self.opts.touser:
            msg.toUsername = self.opts.touser
        if self.opts.subject:
            msg.subject = self.opts.subject

        if self.opts.origin:
            msg.originAddr = Address(self.opts.origin)
        if self.opts.destination:
            msg.destAddr = Address(self.opts.destination)

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

        MessageParser.write(msg, sys.stdout)

if __name__ == '__main__':
    App.run()

