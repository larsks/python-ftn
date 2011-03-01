
#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app
import fidonet.message

class App (fidonet.app.AppUsingFiles,
        fidonet.app.AppUsingAddresses,
        fidonet.app.AppUsingNames):
    logtag = 'fidonet.editmsg'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-k', '--kludge', action='append', default=[])
        p.add_option('-s', '--subject')
        p.add_option('-T', '--time')
        p.add_option('-A', '--area')
        p.add_option('-g', '--flag', action='append',
                default=[])
        p.add_option('--originline', '--oline')
        p.add_option('--disk', action='store_false',
                dest='packed')
        p.add_option('--packed', action='store_true',
                dest='packed')
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
        if self.opts.time:
            msg.dateTime = self.opts.time
            self.log.debug('set dateTime = %s' % msg.dateTime)

        for f in self.opts.flag:
            if f.startswith('!'):
                msg.attributeWord[f[1:]] = False
            else:
                msg.attributeWord[f] = True

        if self.opts.area:
            msg.body.area = self.opts.area

        for k in self.opts.kludge:
            k_name, k_val = k.split(' ', 1)
            msg.body.klines[k_name] = msg.body.klines.get(k_name, []) + [k_val]

        if self.opts.debug:
            import pprint
            pprint.pprint(msg, stream=sys.stderr)

        if name == '<stdin>':
            msg.write(sys.stdout)
        else:
            src.seek(0)
            msg.write(src)
            src.close()

if __name__ == '__main__':
    App.run()

