import os
import sys
import time

from fidonet import Address, MessageFactory
from fidonet.formats import *
import fidonet.app

class App(fidonet.app.AppUsingFiles, fidonet.app.AppUsingAddresses):
    logtag = 'fidonet.pack'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('--stdout', action='store_true')
        p.add_option('-B', '--binkd', action='store_true')
        return p

    def handle_args (self, args):
        if not self.opts.origin:
            self.opts.origin = self.get('fidonet', 'address')
            if self.opts.origin is None:
                self.log.error('Missing origin address.')
                sys.exit(1)

        if not self.opts.destination:
            self.log.error('Missing destination address.')
            sys.exit(1)

        pkt = fsc0048packet.PacketParser.create()

        pkt.origAddr = Address(self.opts.origin)
        pkt.destAddr = Address(self.opts.destination)
        pkt.time = time.localtime()

        self.messages = []
        self.for_each_arg(self.pack_msg, args, ctx=pkt)

        if self.opts.binkd and not self.opts.destdir:
            try:
                self.opts.destdir = self.cfg.get('binkd', 'outbound')
            except:
                self.log.error('unable to determine binkd outbound directory')
                sys.exit(1)
        elif not self.opts.destdir:
            self.opts.destdir = '.'

        if self.opts.output:
            outname = self.opts.output
            out = open(outname, 'w')
        elif self.opts.stdout:
            outname = '<stdout>'
            out = sys.stdout
        else:
            outname = os.path.join(self.opts.destdir, '%s.out' %
                    pkt.destAddr.hex)
            out = open(outname, 'w')

        pkt.write(out)
        pkt.write_messages(out, self.messages)
        pkt.write_eop(out)

        self.log.info('packed %d messages into %s.' % (len(self.messages), outname))

    def pack_msg(self, src, name, ctx=None):
        pkt = ctx

        msg = MessageFactory(src)
        self.messages.append(msg)
        self.log.info('packed message from %s @ %s to %s @ %s' %
                (msg.fromUsername, msg.origAddr, msg.toUsername,
                    msg.destAddr))

if __name__ == '__main__':
    App.run()

