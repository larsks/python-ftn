import os
import sys
import socket
import cPickle as pickle
import time
import struct
import pprint

from sqlalchemy.orm.exc import *

import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag
from fidonet.binkp import BinkpConnection, ConnectionClosed

class NoAddressListed (Exception):
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
        p.add_option('-T', '--retry-failed', action='store_true')
        p.add_option('--retry-only')
        return p

    def setup_nodelist (self):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist

        self.log.debug('using nodelist = %s' % self.opts.nodelist)
        nl = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nl.setup()
        self.session = nl.broker()

    def setup_results(self):
        self.results = {}

        if self.opts.output \
                and not self.opts.noload \
                and os.path.exists(self.opts.output):
            self.results = pickle.load(open(self.opts.output))

    def handle_args(self, args):
        self.opts.port = int(self.opts.port)
        self.opts.interval = int(self.opts.interval)

        self.setup_nodelist()
        self.setup_results()

        nodes = []
        if args:
            for addr in args:
                try:
                    node = self.session.query(Node).filter(
                            Node.address == addr).one()
                    nodes.append(node)
                except NoResultFound:
                    self.log.error('%s: skipped: does not exist in nodelist' % addr)
        else:
            nodes = self.session.query(Node).join(
                    'flags').filter(Flag.flag_name == 'IBN')

        for node in nodes:
            if node.address in self.results:
                if not self.opts.retry_failed \
                        or not '__failed__' in self.results[node.address]:
                    self.log.info('%s: already probed' % node.address)
                    continue

            self.probe(node)
            if self.results and self.opts.output and not self.opts.noincremental:
                pickle.dump(self.results, open(self.opts.output, 'w'))

        if self.results and self.opts.output:
            pickle.dump(self.results, open(self.opts.output, 'w'))

    def probe(self, node):
        self.log.info('probing node %s' % node.address)
        ndinfo = {'__ftnaddress__': node.address,
                '__checked__': time.time()}

        try:
            inet = node.inet('IBN')
            self.log.debug('%s: got address = %s' % (node.address, inet))
            if inet is None:
                raise NoAddressListed()

            c = BinkpConnection(inet.split(':'), timeout=self.opts.timeout)
            c.connect()
            self.read_binkp_info(c, ndinfo)
        except ConnectionClosed:
            self.log.error('%s: remote end closed connection' %
                    node.address)
            ndinfo['__failed__'] = 'disconnected'
        except NoAddressListed:
            self.log.error('%s: no address listed in nodelist' %
                    node.address)
            ndinfo['__failed__'] = 'address'
        except socket.timeout:
            self.log.error('%s: connection timed out' % node.address)
            ndinfo['__failed__'] = 'timeout'
        except socket.gaierror, detail:
            self.log.error('%s: hostname lookup failed: %s' % (node.address,
                detail))
            ndinfo['__failed__'] = 'hostname'
        except socket.error, detail:
            self.log.error('%s: connection failed: %s' % (node.address,
                detail))
            ndinfo['__failed__'] = 'socket: %s' % str(detail)
        except Exception, detail:
            self.log.error('%s: an unknown error occurred: %s' % (
                node.address, detail))
            ndinfo['__failed__'] = 'unknown: %s' % str(detail)

            if self.opts.debug:
                raise

        self.results[ndinfo['__ftnaddress__']] = ndinfo

    def read_binkp_info(self, c, ndinfo):
        seq = 0
        c.send_cmd_frame('M_NUL', 'SYS BINKPROBE')
        c.send_cmd_frame('M_NUL', 'ZYZ binkd statistics robot')
        c.send_cmd_frame('M_ADR', '0:0/0@fidonet')
        while True:
            frame = c.read_frame()

            if frame['command']:
                self.log.debug('received command %(cmd_id)s, data = %(data)s' % frame)
                if frame['cmd_id'] == 'M_NUL':
                    try:
                        k,v = frame['data'].split(None, 1)
                    except ValueError:
                        k = 'unknown_%d' % seq
                        v = frame['data']
                        seq += 1

                    if k in ndinfo:
                        ndinfo[k] = [ndinfo[k], v]
                    else:
                        ndinfo[k] = v
                elif frame['cmd_id'] == 'M_ADR':
                    ndinfo['AKA'] = frame['data'].split()
                    break
                else:
                    self.log.debug('exit loop on cmdid = %s' % frame['cmd_id'])
                    break

        c.send_cmd_frame('M_EOB')

if __name__ == '__main__':
    App.run()

