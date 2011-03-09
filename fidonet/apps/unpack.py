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
        p.add_option('-D', '--output-directory',
                default='.')
        p.add_option('-m', '--message')
        p.add_option('--disk', action='store_false',
                dest='packed')
        p.add_option('--packed', action='store_true',
                dest='packed')

        p.set_default('packed', True)
        return p

    def handle_args(self, args):
        if self.opts.message:
            self.opts.message = [int(x) for x in self.opts.message.split(',')]

        self.gtotal = 0
        self.for_each_arg(self.unpack, args)
        self.log.info('Unpacked %d messages total.' % self.gtotal)

    def unpack(self, src, name, ctx):
        pkt = fidonet.PacketFactory(src)

        for count, msg in enumerate(pkt.messages):
            if self.opts.message and not count in self.opts.message:
                continue

            msgfile = next_message(self.opts.output_directory)
            fd = open(msgfile, 'w')

            if self.opts.packed:
                packedmessage.MessageParser.write(msg,fd)
            else:
                diskmessage.MessageParser.write(msg, fd)
            fd.close()
            self.log.info('wrote message %d from %s to %s' % (
                count, name, msgfile))

        self.log.info('Unpacked %d messages from %s into %s.' % (
                count+1, name, self.opts.output_directory))
        self.gtotal += count+1

if __name__ == '__main__':
    App.run()

