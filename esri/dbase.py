import datetime
import sys

from esri.utils import binread, binread_first

class DBase(object):
    DBASE_LEVEL5 = 3
    DBASE_LEVEL7 = 4

    _MASK_GET_VERSION = 0b00000111
    _MASK_HAS_MEMO    = 0b00001000
    _MASK_HAS_SQLT    = 0b00010000

    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, "rb")

        self.version = 0
        self.has_memo, self.has_sqlt = False, False
        self.last_update = None

        self._read_header()

    def _read_header(self):
        sig = binread_first(self.fd, "<b")
        self.version = sig & self._MASK_GET_VERSION
        if self.version != self.DBASE_LEVEL5:
            sys.stderr.write("Opening non supported dbase file\n")

        self.has_memo = bool((sig & self._MASK_HAS_MEMO) >> 3)
        self.has_sqlt = bool((sig & self._MASK_HAS_SQLT) >> 4)

        year, month, day = binread(self.fd, "<bbb")
        self.last_update = datetime.date(year + 1900, month, day)

if __name__ == '__main__':
    d = DBase(sys.argv[1])
    print "Version: %d" % d.version
    print "Last update: %s" % d.last_update
    print "Has memo: %s" % d.has_memo
    print "Has SQL table: %s" % d.has_sqlt
