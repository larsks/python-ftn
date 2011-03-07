import os
import tempfile
import glob
import errno

from sqlalchemy.sql import and_, or_, not_

import fidonet
import fidonet.app
from fidonet.nodelist import Nodelist, Node

class App(fidonet.app.AppUsingFiles):
    logtag = 'fidonet.indexnl'

    def handle_args(self, args):
        nodelists = []

        if self.opts.output is None:
            nl_base_path = list(self.get_data_paths('fidonet', 'nodelist'))[0]
            self.opts.output = '%s.idx' % nl_base_path

        for nl_base_path in self.get_data_paths('fidonet', 'nodelist'):
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
        tmp = tempfile.NamedTemporaryFile(
                dir=os.path.dirname(self.opts.output))

        self.log.debug('output file is %s' % self.opts.output)
        self.log.debug('tmp file is %s' % tmp.name)

        nl = Nodelist('sqlite:///%s' % tmp.name)
        nl.setup(create=True)
        session = nl.broker()

        for nodelist in nodelists:
            self.index_one_nodelist(session, nodelist)

        self.log.info('creating nodelist index %s' % self.opts.output)
        os.rename(tmp.name, self.opts.output)

        try:
            tmp.close()
        except OSError, detail:
            if detail.errno == errno.ENOENT:
                pass
            else:
                raise

    def index_one_nodelist(self, session, nodelist):
        addr = fidonet.Address()
        hubs = []
        host = None

        self.log.info('indexing %s' % nodelist)

        for line in open(nodelist):
            if line.startswith(';'):
                continue

            node = fidonet.nodelist.Node()
            node.from_nodelist(line, addr)

            if node.node is None:
                continue

            if node.kw == 'hub':
                hubs.append(node)

            session.add(node)

        self.log.debug('committing changes')
        session.commit()

        self.log.debug('updating hub information')
        for hub in hubs:
            session.execute(
                Node.__table__.update(and_(
                    Node.net == hub.net,
                    Node.node != hub.node,
                    Node.node !=0),
                    dict(hub_id=hub.id)))

        self.log.debug('committing changes')
        session.commit()

if __name__ == '__main__':
    App.run()

