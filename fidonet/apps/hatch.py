import os
import sys
import time
import binascii

import fidonet.app

tic_template = '''Area %(area)s
Origin %(origin)s
From %(origin)s
File %(filename)s
Desc %(description)s
CRC %(checksum)s
Created by python-ftn
Size %(size)s
Date %(now)s
Pw %(password)s'''

class App (fidonet.app.AppUsingAddresses):

    def create_parser(self):
        p = super(App, self).create_parser()

        p.add_option('-A', '--area')
        p.add_option('-D', '--description')
        p.add_option('-P', '--password', default='')

        return p

    def handle_args (self, args):
        if not self.opts.origin:
            self.opts.origin = self.get('fidonet', 'address')
            if self.opts.origin is None:
                self.log.error('Missing origin address.')
                sys.exit(1)
        
        srcfile_path = args.pop(0)
        srcfile_name = os.path.basename(srcfile_path)

        fd = open(srcfile_path)
        crc = binascii.crc32(fd.read()) & 0xffffffff
        srcfile_size = fd.tell()
        now = int(time.time())

        print tic_template % {
                'area': self.opts.area,
                'origin': self.opts.origin,
                'filename': srcfile_name,
                'description': self.opts.description,
                'checksum': '%08X' % crc,
                'size': srcfile_size,
                'now': now,
                'password': self.opts.password
                }

if __name__ == '__main__':
    App.run()

