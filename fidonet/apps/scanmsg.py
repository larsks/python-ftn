#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app
import fidonet.message

class App (fidonet.app.App):
    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-b', '--show-body', action='store_true')
        return p

    def handle_args(self, args):

        for msgfile in args:
            msg = fidonet.MessageFactory(fd=open(msgfile))

            print 'From: %(fromUsername)s @ %(origNet)s/%(origNode)s' % msg
            print 'To: %(toUsername)s @ %(destNet)s/%(destNode)s' % msg
            print 'Subject: %(subject)s' % msg
            print 'Flags:',
            for k,v in msg.attributeWord.items():
                if v:
                    print k.upper(),
            print
            print

            if self.opts.show_body:
                if self.opts.debug:
                    import pprint
                    pprint.pprint(msg.body)
                else:
                    print msg.body.render()

if __name__ == '__main__':
    App.run()

