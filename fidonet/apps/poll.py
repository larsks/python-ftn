import os

import fidonet
import fidonet.app

class App (fidonet.app.App):
    '''Creates a BinkD style poll file for all addresses specified on the
    command line.  For example, if you run::
        
        $ ftn-poll 1:322/761 1:123/500

    This script will create two poll files::

        $ ls
        007b01f4.ilo
        014202f9.ilo

    If you have configured a path to your binkd outbound directory in
    ``fidonet.cfg``, ftn-poll will create poll files there; otherwise it
    will use your current directory.'''
    
    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-C', '--crash', action='store_const',
                dest='mode', const='c')
        p.add_option('-I', '--immediate', action='store_const',
                dest='mode', const='i')
        p.add_option('-D', '--direct', action='store_const',
                dest='mode', const='d')
        p.add_option('-F', '--normal', action='store_const',
                dest='mode', const='f')

        p.set_default('mode', 'f')
        return p

    def handle_args(self, args):
        outb = self.get('binkd', 'outbound')
        if outb is None:
            outb = '.'

        for addr in args:
            addr = fidonet.Address(addr)
            self.log.info('creating poll for %s.' % addr)
            poll = os.path.join(outb, '%s.%slo' % (addr.hex, self.opts.mode))
            self.log.debug('poll file = %s' % poll)
            open(poll, 'w').close()

if __name__ == '__main__':
    App.run()

