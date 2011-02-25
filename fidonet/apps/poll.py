import fidonet
import fidonet.app

class App (fidonet.app.App):
    '''Creates a BinkD style poll file for all addresses specified on the
    command line.  For example, if you run::
        
        $ ftn-poll 1:322/761 1:123/500

    This script will create two poll files::

        $ ls
        007b01f4.out
        014202f9.out

    If you have configured a path to your binkd outbound directory in
    ``fidonet.cfg``, ftn-poll will create poll files there; otherwise it
    will use your current directory.'''

    def handle_args(self, args):
        try:
            outb = self.cfg.get('binkd', 'outbound')
        except:
            outb = '.'

        for addr in args:
            addr = fidonet.Address(addr)
            self.log.info('creating poll for %s.' % addr)
            open('%s.out' % addr.hex, 'w').close()

if __name__ == '__main__':
    App.run()

