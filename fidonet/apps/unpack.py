import os

import fidonet
import fidonet.app
import fidonet.message

def next_message(dir, start=1):
    count=start
    while True:
        msgpath = os.path.join(dir, '%d.msg' % count)
        if not os.path.exists(msgpath):
            return msgpath

        count += 1

class App(fidonet.app.App):
    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-d', '--output-directory')
        return p

    def handle_args(self, args):
        gtotal = 0

        for pktfile in args:
            pkt = fidonet.PacketFactory(fd=open(args.pop(0)))

            count = 0
            while True:
                try:
                    m = fidonet.MessageFactory(pkt.messages)
                    fd = open(next_message(self.opts.output_directory), 'w')
                    fidonet.message.MessageParser.write(m, fd)
                    fd.close()
                    count += 1
                except fidonet.EndOfData:
                    break

            self.log.info('Unpacked %d messages from %s into %s.' % (
                    count, pktfile, self.opts.output_directory))
            gtotal += count

        self.log.info('Unpacked %d messages total.' % gtotal)

if __name__ == '__main__':
    App.run()

