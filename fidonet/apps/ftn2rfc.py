import os
import sys
import email.message

import bitstring

import fidonet
import fidonet.app

class App(fidonet.app.App):
    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-z', '--zone')
        return p

    def handle_args(self, args):
        if self.opts.zone is None:
            try:
                myaddr = fidonet.Address(self.cfg.get('fidonet', 'address'))
                self.opts.zone = myaddr.zone
            except:
                pass
        if args:
            src = open(args.pop(0))
        else:
            src = bitstring.ConstBitStream(bytes=sys.stdin.read())

        ftnmsg = fidonet.MessageFactory(src)
        rfcmsg = email.message.Message()

        origAddr = ftnmsg.origAddr
        destAddr = ftnmsg.destAddr

        origAddr.zone = self.opts.zone
        destAddr.zone = self.opts.zone

        rfcmsg['From'] = '@'.join([
                ftnmsg.fromUsername.replace(' ', '_'),
                origAddr.rfc])
        rfcmsg['To'] = '@'.join([
                ftnmsg.toUsername.replace(' ', '_'),
                destAddr.rfc])
        rfcmsg['Subject'] = ftnmsg.subject

        if ftnmsg.body.area is not None:
            rfcmsg['Newsgroups'] = ftnmsg.body.area

        for k in ftnmsg.body['klines'].keys():
            for v in ftnmsg.body['klines'][k]:
                rfcmsg['X-FTN-Kludge'] = '%s %s' % (k,v)

        rfcmsg.set_payload(ftnmsg.body.text)

        print rfcmsg.as_string()

if __name__ == '__main__':
    App.run()

