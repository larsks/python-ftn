import os
import sys
import socket
import struct

DEFAULT_BINKP_PORT = 24554

cmd_names = {
    'M_NUL'   : 0,
    'M_ADR'   : 1,
    'M_PWD'   : 2,
    'M_OK'    : 4,
    'M_FILE'  : 3,
    'M_EOB'   : 5,
    'M_GOT'   : 6,
    'M_ERR'   : 7,
    'M_BSY'   : 8,
    'M_GET'   : 9,
    'M_SKIP'  : 10,
    }

cmd_ids = dict((v,k) for k,v in cmd_names.iteritems())

class ConnectionClosed(Exception):
    pass

class BinkpConnection (object):

    def __init__ (self, addr, timeout=None):
        try:
            self.addr, self.port = addr
        except ValueError:
            (self.addr,) = addr
            self.port = DEFAULT_BINKP_PORT

        self.timeout = timeout

    def connect(self):
        self.ip = socket.gethostbyname(self.addr)
        s = socket.socket()
        self.sock = s

        if self.timeout:
            s.settimeout(float(self.timeout))

        s.connect((self.addr, int(self.port)))

    def read_bytes(self, want):
        bytes = self.sock.recv(want)

        while len(bytes) < want:
            more = self.sock.recv(want - len(bytes))
            if not more:
                raise ConnectionClosed()
            bytes += more

        return bytes

    def read_frame (self):
        bytes = self.read_bytes(2)
        frame_header = struct.unpack('>H', bytes)[0]
        cmd_frame = frame_header & 0x8000
        data_len = frame_header & ~0x8000

        if cmd_frame:
            cmd_id = struct.unpack('b', self.read_bytes(1))[0]
            cmd_id = cmd_ids[cmd_id]
            data = self.read_bytes(data_len - 1)
        else:
            cmd_id = None
            data = self.read_bytes(data_len)

        return {'command': bool(cmd_frame),
                'cmd_id': cmd_id,
                'data': data }

    def send_cmd_frame(self, cmd_id, data=''):
        cmd_id = cmd_names[cmd_id]
        data = struct.pack('b', cmd_id) + data
        data_len = len(data)
        frame_header = data_len | 0x8000
        self.sock.sendall(struct.pack('>H', frame_header))
        self.sock.sendall(data)

    def send_data_frame(self, data):
        data_len = len(data)
        self.sock.sendall(struct.pack('>H', data_len))
        self.sock.sendall(data)

    def disconnect(self):
        self.sock.close()

if __name__ == '__main__':

    b = BinkpConnection((sys.argv[1],), timeout=10)
    b.connect()

    b.send_cmd_frame('M_PWD', '-')

    while True:
        frame = b.read_frame()
        print frame
        if frame['cmd_id'] == 'M_OK':
            break

    b.send_cmd_frame('M_EOB')
    b.read_frame()
    b.disconnect()

