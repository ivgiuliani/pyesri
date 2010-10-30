from esri.utils import binread, binread_first

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

class BoundingBox(object):
    X_MIN, Y_MIN, X_MAX, Y_MAX = 0, 1, 2, 3

    def __init__(self):
        self.bbox = [None] * 4

    def read(self, fd):
        self.bbox = binread(fd, "<dddd")

    def get_x_min(self):
        return self.bbox[self.X_MIN]

    def get_x_max(self):
        return self.bbox[self.X_MAX]

    def get_y_min(self):
        return self.bbox[self.Y_MIN]

    def get_y_max(self):
        return self.bbox[self.Y_MAX]

    x_min = property(get_x_min)
    x_max = property(get_x_max)
    y_min = property(get_y_min)
    x_max = property(get_y_max)

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

    def __repr__(self):
        return "<Shape:%s>" % resolve_shape_name(self.shape_type)

    def read(self, fd):
        raise NotImplementedError

class BasicShape(Shape):
    def __str__(self):
        stradd = self.__str_more__()
        if stradd:
            stradd = " %s" % stradd
        return "%d:%s%s" % (self.record_id,
                            resolve_shape_name(self.shape_type),
                            stradd)

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

class PointShape(BasicShape):
    shape_type = SHAPE_TYPE_POINT
    read_fmt = "<dd"
    read_fmt_field_mapping = [ "x", "y" ]

class PolyLineShape(BasicShape):
    shape_type = SHAPE_TYPE_POLYLINE

    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.bounding_box = BoundingBox()
        self.numparts = 0
        self.numpoints = 0
        self.parts, self.points = [], []

    def read(self, fd):
        self.bounding_box.read(fd)
        self.numparts = binread_first(fd, "<i")
        self.numpoints = binread_first(fd, "<i")

        self.parts = binread(fd, "<" + "i" * self.numparts)
        self.points = [binread(fd, PointShape.read_fmt) for item in range(self.numpoints)]

    def __str_more__(self):
        return "%d parts, %d points" % (self.numparts, self.numpoints)

class PolygonShape(PolyLineShape):
    shape_type = SHAPE_TYPE_POLYGON

class MultiPointShape(BasicShape):
    shape_type = SHAPE_TYPE_MULTIPOINT

    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.bounding_box = BoundingBox()
        self.numpoints = 0
        self.self.points = []

    def read(self, fd):
        self.bounding_box.read(fd)
        self.numparts = binread_first(fd, "<i")
        self.numpoints = binread_first(fd, "<i")
        self.points = [binread(fd, PointShape.read_fmt) for item in range(self.numpoints)]

    def __str_more__(self):
        return "%d points" % (self.numpoints, )

class PointZShape(BasicShape):
    shape_type = SHAPE_TYPE_POINTZ
    read_fmt = "<dddd"
    read_fmt_mapping = [ "x", "y", "z", "m" ]

class PolyLineZShape(PolyLineShape):
    shape_Type = SHAPE_TYPE_POLYLINEZ

    def __init__(self, *args, **kwargs):
        PolyLineShape.__init__(self, *args, **kwargs)
        self.zrange = [0, 0]
        self.zvalues = []
        self.mrange = [0, 0]
        self.measures = []

    def read(self, fd):
        PolyLineShape.read(self, fd)
        self.zrange = binread(fd, "<dd")
        self.zvalues = binread(fd, "<" + "d" * self.numpoints)
        self.mrange = binread(fd, "<dd")
        self.measures = binread(fd, "<" + "d" * self.numpoints)

class PolygonZShape(PolyLineZShape):
    shape_type = SHAPE_TYPE_POLYGONZ

class MultiPointZShape(BasicShape):
    shape_type = SHAPE_TYPE_MULTIPOINTZ

    def __init__(self, *args, **kwargs):
        self.bounding_box = BoundingBox()
        self.numpoints = 0
        self.points = []
        self.zrange = [0, 0]
        self.zvalues = []
        self.mrange = [0, 0]
        self.measures = []

    def read(self, fd):
        self.bounding_box.read(fd)
        self.numpoints = binread_first(fd, "<i")
        self.points = [binread(fd, PointShape.read_fmt) for item in range(self.numpoints)]
        self.zrange = binread(fd, "<dd")
        self.zvalues = binread(fd, "<" + "d" * self.numpoints)
        self.mrange = binread(fd, "<dd")
        self.measures = binread(fd, "<" + "d" * self.numpoints)

class PointMShape(BasicShape):
    shape_type = SHAPE_TYPE_POINTM
    read_fmt = "<ddd"
    read_fmt_field_mapping = [ "x", "y", "m" ]

class PolyLineMShape(PolyLineShape):
    shape_type = SHAPE_TYPE_POLYLINEM

    def __init__(self, *args, **kwargs):
        PolyLineShape.__init__(self, *args, **kwargs)
        self.mrange = [0, 0]
        self.measures = []

    def read(self, fd):
        PolyLineShape.read(self, fd)
        self.mrange = binread(fd, "<dd")
        self.measures = binread(fd, "<" + "d" * self.numpoints)

class PolygonMShape(PolyLineMShape):
    shape_type = SHAPE_TYPE_POLYGON

class MultiPointMShape(BasicShape):
    shape_type = SHAPE_TYPE_MULTIPOINTM

    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.bounding_box = BoundingBox()
        self.numpoints = 0
        self.points = []
        self.mrange = [0, 0]
        self.measures = []

    def read(self, fd):
        self.bounding_box.read(fd)
        self.numpoints = binread_first(fd, "<i")
        self.points = [binread(fd, PointShape.read_fmt) for item in range(self.numpoints)]
        self.mrange = binread(fd, "<dd")
        self.measures = binread(fd, "<" + "d" * self.numpoints)

class MultiPatchShape(BasicShape):
    shape_type = SHAPE_TYPE_MULTIPATCH
    # TODO

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

