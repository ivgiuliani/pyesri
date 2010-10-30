import struct

def binread(fd, fmt):
    return struct.unpack_from(fmt, fd.read(struct.calcsize(fmt)))

def binread_first(fd, fmt):
    return binread(fd, fmt)[0]


