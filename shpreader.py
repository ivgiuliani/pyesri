#!/usr/bin/env python

import sys
import struct

import shapes
from utils import binread, binread_first

class ShapeFile(object):
    SHP_FILE_CODE = 9994

    def __init__(self, filename):
        self.filename = filename
        
        self.shp_filelength = 0
        self.shp_version = 0
        self.shp_shape_type = 0
        self.shp_bbox_xmin, self.shp_bbox_xmax = 0, 0
        self.shp_bbox_ymin, self.shp_bbox_ymax = 0, 0
        self.shp_bbox_zmin, self.shp_bbox_zmax = 0, 0
        self.shp_bbox_mmin, self.shp_bbox_mmax = 0, 0

        self.fd = open(filename, "rb")
        self.get_header()

    def __iter__(self):
        return self.get_record()

    def next(self):
        rec = self.get_record()
        if not rec:
            raise StopIteration

    def get_header(self):
        prolog = binread(self.fd, ">iiiiii")
        # only the first field is used and has a fixed value
        if prolog[0] != self.SHP_FILE_CODE:
            print "warning: wrong file code"
        self.shp_filelength = binread_first(self.fd, ">i")
        self.shp_version = binread_first(self.fd, "<i")
        self.shp_shape_type = binread_first(self.fd, "<i")
        self.shp_bbox_xmin, self.shp_bbox_ymin = binread(self.fd, "<dd")
        self.shp_bbox_xmax, self.shp_bbox_ymax = binread(self.fd, "<dd")
        self.shp_bbox_zmin, self.shp_bbox_zmax = binread(self.fd, "<dd")
        self.shp_bbox_mmin, self.shp_bbox_mmax = binread(self.fd, "<dd")

    def get_record(self):
        bytelength = self.shp_filelength * 2
        while self.fd.tell() < bytelength:
            r_id = binread_first(self.fd, ">i")
            r_content_length = binread_first(self.fd, ">i")
            r_shape = binread_first(self.fd, "<i")

            klass = shapes.type_to_class(r_shape)(r_id)
            klass.read(self.fd)
            yield klass

        if self.fd.tell() != bytelength:
            print "warning: inexeact file end (differs from what header says)"

        # reposition fp to the beginning of file so we can start reading
        # again if we want to
        self.fd.seek(0)
        return

    def print_info(self):
        print "File length: %d" % self.shp_filelength
        print "SHP version: %d" % self.shp_version
        print "Shape type: %s" % shapes.resolve_shape_name(self.shp_shape_type)
        print "Bounding Box X min/max: %d/%d" % (self.shp_bbox_xmin, self.shp_bbox_xmax)
        print "Bounding Box Y min/max: %d/%d" % (self.shp_bbox_ymin, self.shp_bbox_ymax)
        print "Bounding Box Z min/max: %d/%d" % (self.shp_bbox_zmin, self.shp_bbox_zmax)
        print "Bounding Box M min/max: %d/%d" % (self.shp_bbox_mmin, self.shp_bbox_mmax)


if __name__ == '__main__':
    e = ShapeFile(sys.argv[1])
    e.print_info()

    for record in e:
        print repr(record), type(record), str(record)

