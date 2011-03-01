
#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app
import fidonet.message

class App (fidonet.app.AppUsingAddresses, fidonet.app.AppUsingNames):
    logtag = 'fidonet.editmsg'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-s', '--subject')
        return p

    def handle_args(self, args):
        self.for_each_arg(self.edit_msg, args)

    def edit_msg(self, src, name, ctx):
        msg = fidonet.MessageFactory(src)

        if self.opts.to_name:
            self.log.debug('setting to = %s' % self.opts.toname)
            msg.toUsername = self.opts.to_name
        if self.opts.from_name:
            self.log.debug('setting from = %s' % self.opts.from_name)
            msg.fromUsername = self.opts.from_name
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
        else:
            print msg

        if name == '<stdin>':
            msg.write(sys.stdout)
        else:
            src.seek(0)
            msg.write(src)
            src.close()

if __name__ == '__main__':
    App.run()

