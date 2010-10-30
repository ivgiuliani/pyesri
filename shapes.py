from utils import binread, binread_first

SHAPE_TYPE_NULL        = 0
SHAPE_TYPE_POINT       = 1
SHAPE_TYPE_POLYLINE    = 3
SHAPE_TYPE_POLYGON     = 5
SHAPE_TYPE_MULTIPOINT  = 8
SHAPE_TYPE_POINTZ      = 11
SHAPE_TYPE_POLYLINEZ   = 13
SHAPE_TYPE_POLYGONZ    = 15
SHAPE_TYPE_MULTIPOINTZ = 18
SHAPE_TYPE_POINTM      = 21
SHAPE_TYPE_POLYLINEM   = 23
SHAPE_TYPE_POLYGONM    = 25
SHAPE_TYPE_MULTIPOINTM = 28
SHAPE_TYPE_MULTIPATCH  = 31

def resolve_shape_name(shp_type):
    "Resolves shape type constant to shape name"
    return {
        SHAPE_TYPE_NULL        : "Null Shape",
        SHAPE_TYPE_POINT       : "Point",
        SHAPE_TYPE_POLYLINE    : "PolyLine",
        SHAPE_TYPE_POLYGON     : "Polygon",
        SHAPE_TYPE_MULTIPOINT  : "MultiPoint",
        SHAPE_TYPE_POINTZ      : "PointZ",
        SHAPE_TYPE_POLYLINEZ   : "PolyLineZ",
        SHAPE_TYPE_POLYGONZ    : "PolygonZ",
        SHAPE_TYPE_MULTIPOINTZ : "MultiPointZ",
        SHAPE_TYPE_POINTM      : "PointM",
        SHAPE_TYPE_POLYLINEM   : "PolyLineM",
        SHAPE_TYPE_POLYGONM    : "PolygonM",
        SHAPE_TYPE_MULTIPOINTM : "MultiPointM",
        SHAPE_TYPE_MULTIPATCH  : "MultiPatch",
    }[shp_type]

class Shape(object):
    shape_type = SHAPE_TYPE_NULL
    read_fmt = None
    read_fmt_field_mapping = []

    def __init__(self, record_id):
        self.record_id = record_id

    def __str__(self):
        stradd = self.__str_more__()
        if stradd:
            stradd = " %s" % stradd
        return "%d:%s%s" % (self.record_id, resolve_shape_name(self.shape_type), stradd)

    def __str_more__(self):
        "additional str() informations"
        return ""

    def read(self, fd):
        # basic read() for simpler types, you'll probably want
        # to override this
        if self.read_fmt:
            data = binread(fd, read_fmt)
            for idx, item in enumerate(data):
                setattr(self, read_fmt_field_mapping[idx], item)

class NullShape(Shape):
    pass

class PointShape(Shape):
    shape_type = SHAPE_TYPE_POINT
    read_fmt = "<dd"
    read_fmt_field_mapping = [ "x", "y" ]

class PolyLineShape(Shape):
    shape_type = SHAPE_TYPE_POLYLINE

    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.bbox_xmin, \
        self.bbox_ymin, \
        self.bbox_xmax, \
        self.bbox_ymax = [None] * 4

        self.numparts = 0
        self.numpoints = 0
        self.parts, self.points = [], []

    def read(self, fd):
        self.bbox_xmin, \
        self.bbox_ymin, \
        self.bbox_xmax, \
        self.bbox_ymax = binread(fd, "<dddd")

        self.numparts = binread_first(fd, "<i")
        self.numpoints = binread_first(fd, "<i")

        self.parts = binread(fd, "<" + "i" * self.numparts)
        self.points = [binread(fd, PointShape.read_fmt) for item in range(self.numpoints)]

    def __str_more__(self):
        return "%d parts, %d points" % (self.numparts, self.numpoints)

class PolygonShape(Shape):
    shape_type = SHAPE_TYPE_POLYGON

class MultiPointShape(Shape):
    shape_type = SHAPE_TYPE_MULTIPOINT

class PointZShape(Shape):
    shape_type = SHAPE_TYPE_POINTZ

class PolyLineZShape(Shape):
    shape_Type = SHAPE_TYPE_POLYLINEZ

class PolygonZShape(Shape):
    shape_type = SHAPE_TYPE_POLYGONZ

class MultiPointZShape(Shape):
    shape_type = SHAPE_TYPE_MULTIPOINTZ

class PointMShape(Shape):
    shape_type = SHAPE_TYPE_POINTM

class PolyLineMShape(Shape):
    shape_type = SHAPE_TYPE_POLYLINEM

class PolygonMShape(Shape):
    shape_type = SHAPE_TYPE_POLYGON

class MultiPointMShape(Shape):
    shape_type = SHAPE_TYPE_MULTIPOINTM

class MultiPatchShape(Shape):
    shape_type = SHAPE_TYPE_MULTIPATCH

def type_to_class(shp_type):
    return {
        SHAPE_TYPE_NULL        : NullShape,
        SHAPE_TYPE_POINT       : PointShape,
        SHAPE_TYPE_POLYLINE    : PolyLineShape,
        SHAPE_TYPE_POLYGON     : PolygonShape,
        SHAPE_TYPE_MULTIPOINT  : MultiPointShape,
        SHAPE_TYPE_POINTZ      : PointZShape,
        SHAPE_TYPE_POLYLINEZ   : PolyLineZShape,
        SHAPE_TYPE_POLYGONZ    : PolygonZShape,
        SHAPE_TYPE_MULTIPOINTZ : MultiPointZShape,
        SHAPE_TYPE_POINTM      : PointMShape,
        SHAPE_TYPE_POLYLINEM   : PolyLineMShape,
        SHAPE_TYPE_POLYGONM    : PolygonMShape,
        SHAPE_TYPE_MULTIPOINTM : MultiPointMShape,
        SHAPE_TYPE_MULTIPATCH  : MultiPatchShape,
    }[shp_type]

