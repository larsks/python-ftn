import logging
from address import Address

def ftn_address_property(name):
    def _get(self):
        return Address(
                zone = self.get('%sZone' % name),
                net = self.get('%sNet' % name),
                node = self.get('%sNode' % name),
                point = self.get('%sPoint' % name))

    def _set(self, addr):
        self['%sZone' % name] = addr.zone
        self['%sNet' % name] = addr.net
        self['%sNode' % name] = addr.node
        self['%sPoint' % name] = addr.point

    return property(_get, _set)

def commentedfilereader(fd):
    for line in fd:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue

        yield line

