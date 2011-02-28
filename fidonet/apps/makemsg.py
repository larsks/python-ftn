#!/usr/bin/python

import sys
import time
import random

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
        p.add_option('-T', '--time')
        p.add_option('-A', '--area')
        p.add_option('-g', '--flag', action='append',
                default=[])
        p.add_option('--originline', '--oline')
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

        if not self.opts.time:
            self.opts.time = time.strftime('%d %b %y  %H:%M:%S', time.localtime())

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
            self.log.debug('set destAddr = %s' % msg.destAddr)

        if self.opts.time:
            msg.dateTime = self.opts.time
            self.log.debug('set dateTime = %s' % msg.dateTime)

        # set message attributes
        attr = attributeword.AttributeWordParser.create()
        for f in self.opts.flag:
            attr[f] = 1
        msg.attributeWord = attr

        body = msg.body

        if self.opts.area:
            body.area = self.opts.area

        # Generate an origin line if this is an echomail post.
        if not self.opts.originline and self.opts.area:
            try:
                self.opts.originline = '%s (%s)' % (
                        self.cfg.get('fidonet', 'sysname'),
                        Address(self.cfg.get('fidonet', 'address')))
            except:
                pass

        if self.opts.originline:
            body.origin = self.opts.originline

        body.klines['INTL'] = ['%s %s' % (msg.destAddr.pointless,
            msg.origAddr.pointless)]
        body.klines['PID:'] = ['python-ftn']
        body.klines['MSGID:'] = [ '%(origAddr)s ' % msg + '%08x' % self.next_message_id() ]

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

    def next_message_id(self):
        '''so really this should generate message ids from a monotonically
        incrementing sequence...'''
        return random.randint(0,2**32)


if __name__ == '__main__':
    App.run()

