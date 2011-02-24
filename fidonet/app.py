import os
import sys
import optparse
import logging
import ConfigParser

class App (object):
    logtag = 'fidonet'

    def run(class_):
        app = class_()
        return app.main()
    run = classmethod(run)
    
    def main(self):
        self.setup_basic_logging()

        parser = self.create_parser()
        opts, args = parser.parse_args()
        cfg = self.create_config()

        self.opts = opts
        self.cfg = cfg
        self.parser = parser

        self.read_config()
        self.setup_logging()
        self.setup_umask()

        self.log.debug('finished generic setup')

        if self.opts.dump_config:
            self.log.debug('dumping configuration to stdout')
            self.cfg.write(sys.stdout)
            sys.exit()

        self.handle_args(args)

    def setup_basic_logging(self):
        logging.basicConfig(
            datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s %(module)s:%(levelname)s [%(process)s] %(message)s')

    def create_parser(self):
        p = optparse.OptionParser()

        p.add_option('-F', '--config',
                default=os.path.join(
                    os.environ.get('FTN_CONFIG_DIR', '.'), 'fidonet.cfg'),
                help='Path to main configuration file')
        p.add_option('-V', '--verbose',
                action='store_true',
                help='Enable addtional logging.')
        p.add_option('--debug',
                action='store_true',
                help='Turn on debugging output.')
        p.add_option('-O', '--option',
                action='append',
                default=[],
                help='Set configuration options on the command line.')
        p.add_option('--dump-config',
                action='store_true',
                help='Dump configuration to stdout.')

        return p

    def create_config(self):
        cfg = ConfigParser.ConfigParser()
        return cfg

    def read_config(self):
        self.cfg.read(self.opts.config)

        for opt in self.opts.option:
            name, val = opt.split('=',1)
            section, name = name.split(':', 1)

            if not self.cfg.has_section(section):
                self.cfg.add_section(section)

            self.cfg.set(section, name, val)

    def setup_logging(self):
        if self.opts.debug:
            logging.root.setLevel(logging.DEBUG)
        elif self.opts.verbose:
            logging.root.setLevel(logging.INFO)

        self.log = logging.getLogger(self.logtag)

    def setup_umask(self):
        try:
            umask = int(self.cfg.get('fidonet', 'umask'), 8)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError):
            umask = 0022

        self.log.debug('set umask to %04o.' % umask)
        os.umask(umask)

    def handle_args(self, args):
        pass

if __name__ == '__main__':
    App.run()

