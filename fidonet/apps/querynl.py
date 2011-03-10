import os
import tempfile
import glob
import errno

import fidonet
import fidonet.app
from fidonet.nodelist import Nodelist, Node, Flag

class App(fidonet.app.AppUsingFiles):
    '''Query the nodelist index.
    
    Examples
    --------
    
    Find all BinkD capable nodes in 1:322/*::

      $ ftn-querynl -g IBN -a 1:322/*
        1:322/0 : Mass_Net_Central
      1:322/320 : Lost_Crypt
      1:322/759 : The_Zone
      1:322/761 : Somebbs
      1:322/762 : The_American_Connection_BBS
      1:322/767 : EOS_2

    Show verbose information for 1:322/761::

      $ ftn-querynl -a 1:322/761 -v
         Address: 1:322/761
            Name: Somebbs
           SysOp: Lars_Kellogg-stedman
           Phone: 000-0-0-0-0
           BinkD: somebbs.oddbit.com
           Flags: INA:somebbs.oddbit.com IBN
        
        '''

    logtag = 'fidonet.querynl'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-n', '--nodelist')
        p.add_option('-a', '--address')
        p.add_option('-g', '--flag', action='append', default=[])
        p.add_option('-N', '--name')
        p.add_option('-p', '--sysop')
        p.add_option('-r', '--raw', action='store_true')
        return p

    def handle_args(self, args):
        if self.opts.nodelist is None:
            nodelist = self.get_data_path('fidonet', 'nodelist')
            self.opts.nodelist = '%s.idx' % nodelist

        nl = Nodelist('sqlite:///%s' % self.opts.nodelist)
        nl.setup()
        session = nl.broker()

        nodes = session.query(Node).join('flags')

        if self.opts.address:
            if '%' in self.opts.address or '*' in self.opts.address:
                nodes = nodes.filter(
                        Node.address.like(self.opts.address.replace('*', '%')))
            else:
                nodes = nodes.filter(Node.address == self.opts.address)

        if self.opts.sysop:
            if '%' in self.opts.sysop or '*' in self.opts.sysop:
                nodes = nodes.filter(
                        Node.sysop.like(self.opts.sysop.replace('*', '%')))
            else:
                nodes = nodes.filter(Node.sysop == self.opts.sysop)

        if self.opts.name:
            if '%' in self.opts.name or '*' in self.opts.name:
                nodes = nodes.filter(
                        Node.name.like(self.opts.name.replace('*', '%')))
            else:
                nodes = nodes.filter(Node.name == self.opts.name)

        for flag in self.opts.flag:
            if flag.startswith('!'):
                pass
            else:
                nodes = nodes.filter(Flag.flag_name == flag)

        if self.opts.debug:
            print nodes.as_scalar()

        for n in nodes:
            if self.opts.verbose:
                print '%10s: %s' % ('Address', n.address)
                print '%10s: %s' % ('Name', n.name)
                print '%10s: %s' % ('SysOp', n.sysop)
                print '%10s: %s' % ('Phone', n.phone)
                
                if [x for x in n.flags if x.flag_name == 'IBN']:
                    print '%10s: %s' % ('BinkD', n.inet('IBN'))
                if [x for x in n.flags if x.flag_name == 'ITN']:
                    print '%10s: %s' % ('Telnet', n.inet('ITN'))
                print '%10s:' % ('Flags',),
                for flag in n.flags:
                    if flag.flag_val is not None:
                        print '%s:%s' % (flag.flag_name, flag.flag_val),
                    else:
                        print flag.flag_name,
                print
                if self.opts.raw:
                    print '%10s: %s' % ('Raw', n.raw[0].entry)
                print
            else:
                print '%12s : %s' % (n.address, n.name)

if __name__ == '__main__':
    App.run()

