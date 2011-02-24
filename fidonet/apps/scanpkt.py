#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app

class App (fidonet.app.App):
    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-m', '--show-messages', action='store_true')
        p.add_option('-t', '--show-message-text', action='store_true')

        return p

    def handle_args(self, args):

        for pktfile in args:
            pkt = fidonet.PacketFactory(fd=open(pktfile))

            print '=' * 70
            print '%s: ' % pktfile,
            print '%(origZone)s:%(origNet)s/%(origNode)s ->' % pkt,
            print '%(destZone)s:%(destNet)s/%(destNode)s' % pkt,
            print '@ %(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s' % pkt
            print '=' * 70
            print 'V:%(pktVersion)s ' % pkt,
            if pkt.parser == fidonet.packet.fts0001:
                print 'S:FTS-0001',
            else:
                print 'S:FSC-0048 C:%(capWord)s' % pkt,
            print
            print

            if self.opts.show_messages:
                count = 0
                while True:
                    try:
                        msg = fidonet.MessageFactory(pkt.messages)
                        print '[%03d]' % count,
                        print 'From: %(fromUsername)s @ %(origNet)s/%(origNode)s' % msg
                        print '      To: %(toUsername)s @ %(destNet)s/%(destNode)s' % msg
                        print '      Subject: %(subject)s' % msg
                        print '      Flags:',
                        for k,v in msg.attributeWord.items():
                            if v:
                                print k.upper(),
                        print
                        print

                        count += 1
                    except fidonet.EndOfData:
                        break

if __name__ == '__main__':
    App.run()

