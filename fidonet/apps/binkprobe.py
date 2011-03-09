import os
import sys
import bitstring
import socket
import cPickle as pickle
import time

import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag

class ConnectionFailed (Exception):
    pass

class App (fidonet.app.App):

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-t', '--timeout',
                default='10')
        p.add_option('-p', '--port',
                default='24554')
        p.add_option('-i', '--interval',
                default='1')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist

        results = {}
        output = args.pop(0)
        if os.path.exists(output):
            results = pickle.load(open(output))

        self.opts.port = int(self.opts.port)
        self.opts.interval = int(self.opts.interval)

        self.log.debug('using nodelist = %s' % self.opts.nodelist)
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

        for n in nodes:
            if n.address in results:
                self.log.info('%s: skipped: previously seen' % n.address)
                continue

            d = self.probe(n)
            results[d['__ftnaddress__']] = d
            pickle.dump(results, open(output, 'w'))
            time.sleep(self.opts.interval)

        pickle.dump(results, open(output, 'w'))

    def connect(self, node, ndinfo):
        inet = node.inet('IBN')

        if not inet:
            raise ConnectionFailed('no internet address in nodelist' %
                    node.address)

        if ':' in inet:
            addr, port = inet.split(':')
        else:
            addr, port = inet, self.opts.port

        srvraddr = socket.gethostbyname(addr)

        ndinfo['__inet__'] = inet
        ndinfo['__inetaddr__'] = srvraddr

        s = socket.socket()
        s.settimeout(float(self.opts.timeout))
        s.connect((srvraddr, int(port)))

        return s

    def probe(self, node):
        self.log.info('probing node %s' % node.address)
        seq = 0
        ndinfo = {'__ftnaddress__': node.address,
                '__checked__': time.time()}

        try:
            s = self.connect(node, ndinfo)
            self.read_binkp_info(s, node, ndinfo)

            s.close()
        except ConnectionFailed, detail:
            self.log.error('%s: connection failed: %s' % (node.address,
                detail))
            ndinfo['__failed__'] = str(detail)
        except socket.timeout:
            self.log.error('%s: connection timed out' % node.address)
            ndinfo['__failed__'] = 'timeout'
        except socket.gaierror, detail:
            self.log.error('%s: hostname lookup failed: %s' % (node.address,
                detail))
            ndinfo['__failed__'] = str(detail)
        except socket.error, detail:
            self.log.error('%s: connection failed: %s' % (node.address,
                detail))
            ndinfo['__failed__'] = str(detail)
        except Exception, detail:
            self.log.error('%s: an unknown error occurred: %s' %
                    (node.address, detail))
            ndinfo['__failed__'] = str(detail)

        return ndinfo

    def read_binkp_info(self, s, node, ndinfo):
        while True:
            bytes = s.recv(1) + s.recv(1)
            bits = bitstring.BitStream(bytes=bytes)

            cmd = bits.read('bool')
            len = bits.read('uint:15')

            bits = bitstring.BitStream(bytes=s.recv(len))

            if cmd:
                cmdid = bits.read('uint:8')
                if cmdid == 0:
                    data = bits.read('bytes')
                    try:
                        k,v = data.split(None, 1)
                    except ValueError:
                        k = 'unknown_%d' % seq
                        v = data
                        seq += 1
                    ndinfo[k] = v
                else:
                    break

if __name__ == '__main__':
    App.run()

