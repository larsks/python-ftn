#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app
import fidonet.message

class App (fidonet.app.App):
    logtag = 'fidonet.scanmsg'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-t', '--show-text', action='store_true')
        return p

    def handle_args(self, args):
        self.for_each_arg(self.scan_msg, args)

    def scan_msg(self, src, name, ctx):
        msg = fidonet.MessageFactory(src)
        print msg
        print

        if self.opts.show_text:
            if self.opts.debug:
                import pprint
                pprint.pprint(msg.body)
            else:
                print msg.body
            print

if __name__ == '__main__':
    App.run()

