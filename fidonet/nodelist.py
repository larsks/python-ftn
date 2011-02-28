import logging

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

fields = (
        'kw',
        'node',
        'name',
        'location',
        'sysop',
        'phone',
        'speed'
        )

metadata = None
engine = None
broker = None

Base = declarative_base()

class Flag(Base):
    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('nodes.id'))

    flag_name = Column(String)
    flag_val = Column(String)

class Node(Base):
    __tablename__ = 'nodes'

    transform = {
            'kw': lambda x: x.lower()
            }

    id = Column(Integer, primary_key=True)
    kw = Column(String, index=True)
    name = Column(String)
    location = Column(String)
    sysop = Column(String)
    phone = Column(String)
    speed = Column(String)

    zone = Column(Integer, index=True)
    region = Column(Integer, index=True)
    net = Column(Integer, index=True)
    node = Column(Integer)

    address = Column(String, index=True, unique=True)

    flags = relationship(Flag, backref='node')

    def __str__ (self):
        return '<Node %s (%s)>' % (self.address, self.name)

    def __repr__ (self):
        return self.__str__()

    def from_nodelist(self, line, addr):
        cols = line.rstrip().split(',')
        if len(cols) < len(fields):
            return

        for k,v in (zip(fields, cols[:len(fields)])):
            if k in self.transform:
                v = self.transform[k](v)
            setattr(self, k, v)

        if self.kw == 'zone':
            addr.zone = self.node
            addr.region = self.node
            addr.net = self.node
            addr.node = 0
        elif self.kw == 'region':
            addr.region = self.node
            addr.net = self.node
            addr.node = 0
        elif self.kw == 'host':
            addr.net = self.node
            addr.node = 0
        else:
            addr.node = self.node

        self.zone = addr.zone
        self.region = addr.region
        self.net = addr.net
        self.node = addr.node
        self.address = addr.ftn

        logging.debug('parsed node: %s' % self)

        flags = cols[len(fields):]

        for flag in flags:
            if ':' in flag:
                flag_name, flag_val = flag.split(':', 1)
            else:
                flag_name = flag
                flag_val = None

            self.flags.append(Flag(flag_name=flag_name, flag_val=flag_val))


def setup_nodelist(dburi, create=False):
    global metadata
    global engine
    global broker

    metadata = Base.metadata
    engine = create_engine(dburi)

    if create:
        metadata.create_all(engine)

    broker = sessionmaker(bind=engine)

