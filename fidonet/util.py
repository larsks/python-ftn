from address import Address

def ftn_address_property(name):
    def _get(self):
        return Address(
                zone = self.get('%sZone' % name),
                net = self.get('%sNet' % name),
                node = self.get('%sNode' % name))

    def _set(self, addr):
        self['%sZone' % name] = addr.zone
        self['%sNet' % name] = addr.net
        self['%sNode' % name] = addr.node

    return property(_get, _set)


