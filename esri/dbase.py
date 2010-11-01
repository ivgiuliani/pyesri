import datetime
import sys

from esri.utils import binread, binread_first

class DBaseRecord(object):
    def read(self, fd):
        """
        Read the record that starts at the position
        the file descriptor cursor points to
        """
        name = binread_first(fd, "32s")
        return {
            "field_name": name,
        }

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

        self.records_no = 0
        self.header_bytes = 0
        self.record_bytes = 0

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

        self.records_no = binread_first(self.fd, "<i")
        self.header_bytes = binread_first(self.fd, "<h")
        self.record_bytes = binread_first(self.fd, "<h")

        # two empty bytes at this point
        if binread_first(self.fd, "!h") != 0:
            sys.stderr.write("expected empty bytes, found something\n")

        # skip these bytes, we don't need em for reading
        self.fd.seek(64)

    def read_record(self):
        return DBaseRecord().read(self.fd)


if __name__ == '__main__':
    d = DBase(sys.argv[1])
    print "Version: %d" % d.version
    print "Last update: %s" % d.last_update
    print "Has memo: %s" % d.has_memo
    print "Has SQL table: %s" % d.has_sqlt
    print "Number of records in the table: %d" % d.records_no
    print "Number of bytes in the header: %d" % d.header_bytes
    print "Number of bytes in the record: %d" % d.record_bytes

    print d.read_record()

