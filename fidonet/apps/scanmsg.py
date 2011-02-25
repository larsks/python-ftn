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
        p.add_option('-b', '--show-body', action='store_true')
        return p

    def handle_args(self, args):

        for msgfile in args:
            msg = fidonet.MessageFactory(open(msgfile))
            print msg
            print

            if self.opts.show_body:
                if self.opts.debug:
                    import pprint
                    pprint.pprint(msg.body)
                else:
                    print msg.body
                print

if __name__ == '__main__':
    App.run()

