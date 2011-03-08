import os
import errno
import time
import atexit

class AlreadyLocked (Exception):
    pass

class Sequence(object):
    def __init__ (self, path, start=0, locktries=3, lockinterval=1):
        self.path = path
        self.locked = False
        self.start = start
        self.locktries=int(locktries)
        self.lockinterval=float(lockinterval)

        self.valpath = os.path.join(self.path, 'val')
        self.lockpath = os.path.join(self.path, '.lock')

        try:
            os.mkdir(path)
        except OSError, detail:
            if detail.errno == errno.EEXIST:
                pass
            else:
                raise

        try:
            self.lock()
            if not os.path.exists(self.valpath):
                fd = open(self.valpath, 'w')
                fd.write('%d' % start)
                fd.close()
        finally:
            self.unlock()

        atexit.register(self.unlock)

    def _lock(self):
        try:
            os.mkdir(self.lockpath)
            self.locked = True
        except OSError, detail:
            if detail.errno == errno.EEXIST:
                raise AlreadyLocked()
            else:
                raise

    def lock(self):
        tries = 0
        while tries < self.locktries:
            try:
                self._lock()
                return
            except AlreadyLocked:
                time.sleep(self.lockinterval)
                tries += 1

        raise AlreadyLocked()

    def unlock(self):
        if not self.locked:
            return

        os.rmdir(self.lockpath)
        self.locked = False

    def next(self):
        try:
            self.lock()
            fd = open(self.valpath, 'r+')
            try:
                val = int(fd.read())
            except ValueError:
                val = self.start
            fd.seek(0)
            fd.write('%d' % (val+1))
            fd.truncate()
            fd.close()
        finally:
            self.unlock()

        return val

if __name__ == '__main__':
    import sys

    s = Sequence(sys.argv[1])

    for i in range(0,10):
        print s.next()
        time.sleep(float(sys.argv[2]))

