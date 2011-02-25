import os
import sys
import time

from fidonet import Address, MessageFactory
from fidonet.formats import *
import fidonet.app

class App(fidonet.app.App):
    logtag = 'fidonet.pack'

    def create_parser(self):
        p = super(App, self).create_parser()

        p.add_option('--output', '--out')
        p.add_option('-o', '--origin', '--orig')
        p.add_option('-d', '--destination', '--dest')
        p.add_option('--stdout', action='store_true')

        return p

    def handle_args (self, args):
        if not self.opts.origin:
            try:
                self.opts.origin = self.cfg.get('fidonet', 'address')
            except Exception, detail:
                self.log.error('Missing origin address.')
                sys.exit(1)

        if not self.opts.destination:
            self.log.error('Missing destination address.')
            sys.exit(1)

        pkt = fsc0048packet.PacketParser.create()

        pkt.origAddr = Address(self.opts.origin)
        pkt.destAddr = Address(self.opts.destination)
        pkt.time = time.localtime()

        count = 0
        for msgfile in args:
            msg = MessageFactory(open(msgfile))
            pkt.messages.append(packedmessage.MessageParser.build(msg))
            count += 1
            self.log.info('packed message from %s @ %s to %s @ %s' %
                    (msg.fromUsername, msg.origAddr, msg.toUsername,
                        msg.destAddr))

        if self.opts.output:
            outname = self.opts.output
            out = open(outname, 'w')
        elif self.opts.stdout:
            outname = '<stdout>'
            out = sys.stdout
        else:
            outname = '%s.out' % pkt.destAddr.hex
            out = open(outname, 'w')

        pkt.write(out)
        self.log.info('packed %d messages into %s.' % (count, outname))

if __name__ == '__main__':
    App.run()

