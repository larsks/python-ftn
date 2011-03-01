import os
import sys
import time

from fidonet import Address, MessageFactory, Router
from fidonet.nodelist import Node, Nodelist
from fidonet.formats import *
import fidonet.app

class App(fidonet.app.App):
    logtag = 'fidonet.toss'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-o', '--origin', '--orig')
        p.add_option('-d', '--dir')
        p.add_option('-r', '--routes')
        p.add_option('-n', '--nodelist')
        return p

    def handle_args (self, args):
        if not self.opts.origin:
            try:
                self.opts.origin = self.cfg.get('fidonet', 'address')
            except:
                self.log.error('unable to determine origin address.')
                sys.exit(1)

        if not self.opts.dir:
            try:
                self.opts.dir = self.cfg.get('binkd', 'outbound')
            except:
                self.log.error('failed to determine binkd outbound directory.')
                sys.exit(1)

        if not self.opts.routes:
            try:
                self.opts.routes = self.cfg.get('fidonet', 'routes')
            except:
                self.log.error('unable to determine routing policy file.')
                sys.exit(1)

        if not self.opts.nodelist:
            try:
                self.opts.nodelist = '%s.idx' % self.cfg.get('fidonet',
                        'nodelist').split()[0]
            except:
                self.log.error('unable to determine nodelist path.')
                sys.exit(1)

        if not os.path.isdir(self.opts.dir):
            self.log.error('binkd outbound directory "%s" is unavailable.'
                    % self.opts.dir)
            sys.exit(1)
        if not os.path.isfile(self.opts.nodelist):
            self.log.error('nodelist index "%s" is unavailable.' %
                    self.opts.routes)
            sys.exit(1)
        if not os.path.isfile(self.opts.routes):
            self.log.error('routing policy file "%s" is unavailable.' %
                    self.opts.routes)
            sys.exit(1)

        self.opts.origin = Address(self.opts.origin)

        self.log.debug('my origin = %s' % self.opts.origin)
        self.log.debug('target directory = %s' % self.opts.dir)
        self.log.debug('routing policy = %s' % self.opts.routes)
        self.log.debug('nodelist = %s' % self.opts.nodelist)

        nodelist = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nodelist.setup()
        self.router = Router(nodelist, self.opts.routes)
        self.packets = {}
        self.origin = fidonet.Address(self.opts.origin)

        self.for_each_arg(self.toss_pkt, args)

        for pkt in self.packets.values():
            out = os.path.join(self.opts.dir, '%s.out' % pkt.destAddr.hex)
            self.log.info('writing packet for %s to %s.' % (pkt.destAddr,
                out))
            pkt.write(open(out, 'w'))

    def toss_pkt(self, src, name, ctx):
        msg = fidonet.MessageFactory(src)

        if not msg.destAddr.zone:
            msg.destZone = self.origin.zone

        self.log.debug('processing message to %s' % msg.destAddr)

        route = self.router[msg.destAddr]
        dest = route[0]

        if not dest.ftn in self.packets:
            self.log.info('creating new packet for %s' % dest)
            newpkt = fsc0048packet.PacketParser.create()
            newpkt.destAddr = dest
            newpkt.origAddr = fidonet.Address(self.opts.origin)
            self.packets[dest.ftn] = newpkt

        self.log.info('packing message from %s to %s via %s.' % (msg.origAddr,
            msg.destAddr, dest))
        self.packets[dest.ftn].messages.append(packedmessage.MessageParser.build(msg))

if __name__ == '__main__':
    App.run()

