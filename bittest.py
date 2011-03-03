#from fidonet.bitparser import *
#
#s1 = Struct('s1',
#        Field('uidNumber', 'uint:16'),
#        CString('uid'),
#        CString('cn')
#        )
#
#s2 = Struct('s2',
#        Field('address', 'uint:32'),
#        Repeat('users', s1)
#        )
#
#data = s2.unpack_bytes('\x00\x00\x00\x00\x11\x11Lars\x00lars\x00\x22\x22Katie\x00ktfitzg\x00')
#print data
#
import fidonet
from fidonet.formats import *
#
#print 'MESSAGE'
#msg = fidonet.MessageFactory(open('netmail/1.msg'))
#msg.write(open('new.msg', 'w'))
#
print 'PACKET'
pkt = fidonet.PacketFactory(open('multi.pkt'))
#pkt.messages.append(msg)
#pkt.write(open('new.pkt', 'w'))

