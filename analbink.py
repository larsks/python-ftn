import os
import sys
import cPickle as pickle
import pprint
import re

def graph (data, title, key, maxwidth=75):
    print title
    print
    print '%10s |' % key
    print '-----------+------------------------------------------------------------'

    w = maxwidth - 17
    max = 0
    for k,v in data.items():
        if v > max: max = v

    for k,v in data.items():
        line = '#' * (int((v * ((w*1.0)/max)))+1)
        if len(line) > len('%d' % v) + 9:
            line = '%s (%d) ##' % ( '#' * (len(line)-9), v)
        else:
            line = '%s (%d)' % (line, v)
        print '%10s | %s' % (k, line)

data = pickle.load(open(sys.argv[1]))

total = 0
binkd = 0
other = 0
unknown = 0
failed = 0

binkd_idx = {'vers': {},
        'os': {}}

for k,v in data.items():
    total += 1
    if '__failed__' in v:
        failed += 1
    elif 'VER' in v:
        if v['VER'].startswith('binkd'):
            binkd += 1
            try:
                x, vers, os = v['VER'].split()[0].split('/', 2)
                if vers.startswith('1.0a'):
                    vers = '1.0a'
                elif vers.startswith('0.') and int(vers.split('.')[1]) < 9:
                    vers = '0.%s.x' % vers.split('.')[1]
                elif vers.startswith('0.9'):
                    mo = re.match('(\d+\.\d+.\d+)(.*)', vers)
                    vers = mo.group(1)

                binkd_idx['vers'][vers] = binkd_idx['vers'].get(vers, 0) + 1
                binkd_idx['os'][os] = binkd_idx['os'].get(os, 0) + 1
            except ValueError:
                pass
        else:
            other += 1
    else:
        unknown += 1

graph({'binkd': binkd, 'other': other, 'unknown': unknown, 'failed':
    failed}, 'BinkP capable mailers', 'mailer')
print
graph(binkd_idx['vers'], 'BinkD use by version', 'version')
print
graph(binkd_idx['os'], 'BinkD use by operating system', 'os')

