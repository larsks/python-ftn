import os
import sys
import optparse
import logging
import ConfigParser

import bitstring

from fidonet import defaults

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

        self.opts = opts
        self.parser = parser

        self.cfg = self.create_config()
        self.read_config()
        self.defaults = self.set_defaults()

        self.setup_logging()
        self.setup_umask()

        self.log.debug('reading config from %s' % self.opts.config)
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

        p.add_option('--config', '--cf',
                default=defaults.ftn_config_file,
                help='Path to main configuration file.')
        p.add_option('--config-dir',
                default=defaults.ftn_config_dir,
                help='Find configuration files in this directory.')
        p.add_option('--data-dir',
                default=None,
                help='Find data files in this directory.'),
        p.add_option('-v', '--verbose',
                action='store_true',
                help='Enable addtional logging.')
        p.add_option('--debug',
                action='store_true',
                help='Turn on debugging output.')
        p.add_option('--option',
                action='append',
                default=[],
                help='Set configuration options on the command line.')
        p.add_option('--dump-config',
                action='store_true',
                help='Dump configuration to stdout.')

        return p

    def set_defaults(self):
        '''This is called after processing command line options and reading
        the config file.  It is responsible for setting up any default
        values and for adjusting existing config files (e.g., transforming
        relative paths into absolute paths).'''

        if not self.opts.data_dir:
            self.opts.data_dir = self.get('fidonet', 'datadir')
        if not self.opts.data_dir:
            self.opts.data_dir = defaults.ftn_data_dir

        if self.opts.data_dir:
            self.opts.data_dir = os.path.abspath(self.opts.data_dir)
        if self.opts.config_dir:
            self.opts.config_dir = os.path.abspath(self.opts.config_dir)

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

    def get(self, section, option, default=None):
        try:
            return self.cfg.get(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

    def relpath(self, path, dir):
        if path is None:
            return None
        elif path.startswith('/'):
            return path
        else:
            return os.path.join(dir, path)

    def get_cfg_path(self, section, option, default=None):
        try:
            path = self.cfg.get(section, option).split()[0]
            return self.relpath(path, self.opts.config_dir)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

    def get_cfg_paths(self, section, option, default=''):
        for path in self.get(section, option, default).split():
            yield self.relpath(path, self.opts.config_dir)

    def get_data_path(self, section, option, default=None):
        try:
            path = self.cfg.get(section, option).split()[0]
            return self.relpath(path, self.opts.data_dir)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

    def get_data_paths(self, section, option, default=''):
        for path in self.get(section, option, default).split():
            yield self.relpath(path, self.opts.data_dir)

    def handle_args(self, args):
        pass

    def for_each_arg(self, func, args, ctx=None):
        if not args:
            args = ['-']

        for msgfile in args:
            if msgfile == '-':
                msgbits = bitstring.BitStream(bytes=sys.stdin.read())
                msgfile = '<stdin>'
            else:
                msgbits = open(msgfile, 'r+')

            func(msgbits, msgfile, ctx=ctx)

class AppUsingFiles (App):

    def create_parser(self):
        p = super(AppUsingFiles, self).create_parser()
        p.add_option('-O', '--output', '--out',
                metavar='FILE',
                help='Send output to FILE.')
        p.add_option('-D', '--destdir', '--dir',
                metavar='DIR',
                help='Place output files in DIR.')
        return p

class AppUsingAddresses (App):

    def create_parser(self):
        p = super(AppUsingAddresses, self).create_parser()
        p.add_option('-o', '--origin', '--orig',
                metavar='ADDRESS',
                help='Set origin address to ADDRESS.')
        p.add_option('-d', '--destination', '--dest',
                metavar='ADDRESS',
                help='Set destination address to ADDRESS.')
        return p

class AppUsingNames (App):

    def create_parser(self):
        p = super(AppUsingNames, self).create_parser()
        p.add_option('-f', '--from-name', '--from',
                metavar='NAME',
                help='Set sender name to NAME.')
        p.add_option('-t', '--to-name', '--to',
                metavar='NAME',
                help='Set recipient name to NAME.')
        return p

if __name__ == '__main__':
    a = App()
    a.main()


