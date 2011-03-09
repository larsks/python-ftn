import os
import sys
import bitstring
import socket
import cPickle as pickle

import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag

class App (fidonet.app.App):

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-t', '--timeout',
                default='10')
        p.add_option('-p', '--port',
                default='24554')
        p.add_option('-O', '--output', '--out')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist

        nl = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nl.setup()
        session = nl.broker()

        if args:
            nodes = []
            for addr in args:
                nodes.append(session.query(Node).filter(Node.address ==
                        addr).one())
        else:
            nodes = session.query(Node).join('flags').filter(
                    Flag.flag_name == 'IBN')

        results = []
        for n in nodes:
            d = self.connect(n)
            results.append(d)

        if self.opts.output:
            pickle.dump(results, open(self.opts.output, 'w'))
        else:
            import pprint
            pprint.pprint(results)

    def connect(self, node):
        data = {'__address__': node.address}

        inet = node.inet('IBN')
        if not inet:
            data['__failed__'] = 'no address'
            return data

        if ':' in inet:
            addr, port = inet.split(':')
        else:
            addr, port = inet, self.opts.port

        srvraddr = socket.gethostbyname(addr)
        s = socket.socket()
        s.settimeout(float(self.opts.timeout))

        try:
            s.connect((srvraddr, int(port)))

            while True:
                bytes = s.recv(2)
                bits = bitstring.BitStream(bytes=bytes)

                cmd = bits.read('bool')
                len = bits.read('uint:15')

                bits = bitstring.BitStream(bytes=s.recv(len))

                if cmd:
                    cmdid = bits.read('uint:8')
                    if cmdid == 0:
                        k, v = bits.read('bytes').split(None, 1)
                        data[k] = v
                    else:
                        break
            s.close()
            return data
        except socket.timeout:
            data['__failed__'] = 'timeout'
            return data

if __name__ == '__main__':
    App.run()

