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
            self.opts.origin = self.get('fidonet', 'address')

        if not self.opts.dir:
            self.opts.dir = self.get_data_path('binkd', 'outbound')

        if not self.opts.routes:
            self.opts.routes = self.get_cfg_path('fidonet', 'routes')

        if not self.opts.nodelist:
            self.opts.nodelist = '%s.idx' % self.get_data_paths(
                    'fidonet', 'nodelist').next()

        if not self.opts.nodelist:
            sys.log.error('unable to locate a nodelist index')
            sys.exit(1)
        if not os.path.isfile(self.opts.nodelist):
            self.log.error('nodelist index "%s" is unavailable.' %
                    self.opts.routes)
            sys.exit(1)
        if not os.path.isdir(self.opts.dir):
            self.log.error('binkd outbound directory "%s" is unavailable.'
                    % self.opts.dir)
            sys.exit(1)
        if self.opts.routes is not None and not os.path.isfile(self.opts.routes):
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
        self.log.debug('got route = %s' % str(route))
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

