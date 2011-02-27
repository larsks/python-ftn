import os
import sys
import email.message

import bitstring

import fidonet
import fidonet.app

class App(fidonet.app.App):
    def handle_args(self, args):
        if args:
            src = open(args.pop(0))
        else:
            src = bitstring.ConstBitStream(bytes=sys.stdin.read())

        ftnmsg = fidonet.MessageFactory(src)
        rfcmsg = email.message.Message()

        origAddr = ftnmsg.origAddr
        destAddr = ftnmsg.destAddr
        body = ftnmsg.body

        origAddr.zone = 1
        destAddr.zone = 1

        rfcmsg['From'] = '@'.join([
                ftnmsg.fromUsername.replace(' ', '_'),
                origAddr.rfc])
        rfcmsg['To'] = '@'.join([
                ftnmsg.toUsername.replace(' ', '_'),
                destAddr.rfc])
        rfcmsg['Subject'] = ftnmsg.subject

        for k in body['klines'].keys():
            for v in body['klines'][k]:
                rfcmsg['X-FTN-Kludge'] = '%s %s' % (k,v)

        rfcmsg.set_payload(ftnmsg.body.body)

        print rfcmsg.as_string()

if __name__ == '__main__':
    App.run()

