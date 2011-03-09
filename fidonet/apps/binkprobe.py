import os
import sys
import socket
import cPickle as pickle
import time
import struct
import pprint

import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag
from fidonet.binkp import BinkpConnection

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
        p.add_option('-O', '--output', '--out')
        p.add_option('--noincremental', action='store_true')
        p.add_option('-N', '--noload', action='store_true')
        p.add_option('-I', '--inet', action='store_true')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist

        results = {}
        if self.opts.output \
                and not self.opts.noload \
                and os.path.exists(self.opts.output):
            results = pickle.load(open(self.opts.output))

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
            if self.opts.debug:
                pprint.pprint(d)

            results[d['__ftnaddress__']] = d
            if self.opts.output and not self.opts.noincremental:
                pickle.dump(results, open(self.opts.output, 'w'))
            time.sleep(self.opts.interval)

        if self.opts.output:
            pickle.dump(results, open(self.opts.output, 'w'))

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
            self.log.error('%s: an unknown error occurred: %s' % (
                node.address, detail))
            ndinfo['__failed__'] = str(detail)

            if self.opts.debug:
                raise

        return ndinfo

    def read_bytes(self, s, want):
        bytes = s.recv(want)

        while len(bytes) < want:
            print 'want %d, got %d, reading %d' % (
                    want, len(bytes), (want-len(bytes)))
            bytes += s.recv(want - len(bytes))

        return bytes

    def read_frame (self, s):
        bytes = self.read_bytes(s, 2)
        frame_header = struct.unpack('>H', bytes)[0]
        cmd_frame = frame_header & 0x8000
        data_len = frame_header & ~0x8000

        if cmd_frame:
            cmd_id = struct.unpack('B', s.recv(1))[0]
            data = self.read_bytes(s, data_len - 1)

            self.log.debug('received command frame, cmd_id = %d, data = %s'
                    % (cmd_id, data))
        else:
            cmd_id = 0
            data = self.read_bytes(s, data_len)
            self.log.debug('received data frame, length = %d bytes' %
                    data_len)

        return { 'command': bool(cmd_frame),
                'cmd_id': cmd_id,
                'data': data }

    def send_cmd_frame(self, s, cmd_id, data):
        data = struct.pack('b', cmd_id) + data
        data_len = len(data)
        frame_header = data_len | 0x8000

        s.sendall(struct.pack('>H', frame_header))
        s.sendall(data)

        self.log.debug('sent command frame, cmd_id = %d, data = %s' %
                (cmd_id, data))

    def read_binkp_info(self, s, node, ndinfo):
        while True:
            frame = self.read_frame(s)

            if frame['command']:
                if frame['cmd_id'] == 0:
                    try:
                        k,v = frame['data'].split(None, 1)
                    except ValueError:
                        k = 'unknown_%d' % seq
                        v = data
                        seq += 1

                    if k in ndinfo:
                        ndinfo[k] = [ndinfo[k], v]
                    else:
                        ndinfo[k] = v
                elif frame['cmd_id'] == 1:
                    ndinfo['AKA'] = frame['data'].split()

                    self.send_cmd_frame(s, 2, '-')
                elif frame['cmd_id'] == 7:
                    ndinfo['__passreq__'] = True
                    break
                else:
                    self.log.debug('exit loop on cmdid = %d' % frame['cmd_id'])
                    break

if __name__ == '__main__':
    App.run()

