import os
import tempfile
import glob
import errno

import fidonet
import fidonet.app
import fidonet.nodelist

class App(fidonet.app.App):
    logtag = 'fidonet.indexnl'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-o', '--output')
        return p

    def handle_args(self, args):
        nodelists = []

        for nl_base_path in self.cfg.get('fidonet', 'nodelist').split():
            if os.path.exists(nl_base_path):
                nodelists.append(nl_base_path)
                self.log.debug('added nodelist %s' % nl_base_path)
                continue

            entries = glob.glob('%s.[0-9][0-9][0-9]' % nl_base_path)
            if entries:
                nodelists.append(list(sorted(entries))[-1])
                self.log.debug('added nodelist %s' % nodelists[-1])

        self.build_index(nodelists)

    def build_index(self, nodelists):
        if self.opts.output:
            output = self.opts.output
        else:
            output = os.path.join(
                    os.path.dirname(nodelists[0]),
                    'nodeindex.db')
            tmp = tempfile.NamedTemporaryFile(
                    dir=os.path.dirname(output))

        self.log.debug('output file is %s' % output)
        self.log.debug('tmp file is %s' % tmp.name)
        fidonet.nodelist.setup_nodelist('sqlite:///%s' % tmp.name,
                create=True)
        self.session = fidonet.nodelist.broker()

        for nodelist in nodelists:
            self.index_one_nodelist(nodelist)

        os.rename(tmp.name, output)

        try:
            tmp.close()
        except OSError, detail:
            if detail.errno == errno.ENOENT:
                pass
            else:
                raise

    def index_one_nodelist(self, nodelist):
        addr = fidonet.Address()

        self.log.info('indexing %s' % nodelist)

        for line in open(nodelist):
            if line.startswith(';'):
                continue

            node = fidonet.nodelist.Node()
            node.from_nodelist(line, addr)

            if node.node is None:
                continue

            self.session.add(node)

        self.session.commit()

if __name__ == '__main__':
    App.run()

