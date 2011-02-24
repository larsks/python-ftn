
#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app
import fidonet.message

class App (fidonet.app.App):
    def create_parser(self):
        p = super(App, self).create_parser()

        p.add_option('-t', '--toname', '--to')
        p.add_option('-f', '--fromname', '--from')
        p.add_option('-o', '--origin', '--orig')
        p.add_option('-d', '--destination', '--dest')
        p.add_option('-s', '--subject')

        return p

    def handle_args(self, args):

        for msgfile in args:
            fd = open(msgfile, 'r+')
            msg = fidonet.MessageFactory(fd=fd)

            if self.opts.toname:
                self.log.debug('setting to = %s' % self.opts.toname)
                msg.toUsername = self.opts.toname
            if self.opts.fromname:
                self.log.debug('setting from = %s' % self.opts.fromname)
                msg.fromUsername = self.opts.fromname
            if self.opts.origin:
                addr = fidonet.Address(self.opts.origin)
                self.log.debug('setting origin = %s' % addr)
                msg.origAddr = addr
            if self.opts.destination:
                addr = fidonet.Address(self.opts.destination)
                self.log.debug('setting destination = %s' % addr)
                msg.destAddr = addr
            if self.opts.subject:
                self.log.debug('setting subject = %s' % self.opts.subject)
                msg.subject = self.opts.subject

            if self.opts.debug:
                import pprint
                pprint.pprint(msg)

            fd.seek(0)
            fidonet.message.MessageParser.write(msg, fd)
            fd.close()

if __name__ == '__main__':
    App.run()

