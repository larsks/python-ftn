import os

import fidonet
import fidonet.app
from fidonet.formats import *

def next_message(dir, start=1):
    count=start
    while True:
        msgpath = os.path.join(dir, '%d.msg' % count)
        if not os.path.exists(msgpath):
            return msgpath

        count += 1

class App(fidonet.app.App):
    logtag = 'fidonet.unpack'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-d', '--output-directory')
        p.add_option('--disk', action='store_false',
                dest='packed')
        p.add_option('--packed', action='store_true',
                dest='packed')

        p.set_default('packed', True)
        return p

    def handle_args(self, args):
        gtotal = 0

        for pktfile in args:
            pkt = fidonet.PacketFactory(open(pktfile))

            count = 0
            while True:
                try:
                    msg = fidonet.MessageFactory(pkt.messages)
                    msgfile = next_message(self.opts.output_directory)
                    fd = open(msgfile, 'w')

                    if self.opts.packed:
                        packedmessage.MessageParser.write(msg,fd)
                    else:
                        diskmessage.MessageParser.write(msg, fd)
                    fd.close()
                    self.log.debug('wrote message from %s to %s' % (
                        pktfile, msgfile))
                    count += 1
                except fidonet.EndOfData:
                    break

            self.log.info('Unpacked %d messages from %s into %s.' % (
                    count, pktfile, self.opts.output_directory))
            gtotal += count

        self.log.info('Unpacked %d messages total.' % gtotal)

if __name__ == '__main__':
    App.run()

