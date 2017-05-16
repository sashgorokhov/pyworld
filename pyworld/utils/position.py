from pyworld.utils import auto_representer, attrdict

__all__ = ['Point', 'Size', 'PointSize', 'Rect']


class Base(attrdict.TupledAttrDict):
    pass


@auto_representer
class Point(Base):
    x = None
    y = None

    def __init__(self, x, y):
        if x is None:
            raise ValueError('x is None')
        if y is None:
            raise ValueError('y is None')
        Base.__init__(self, x=x, y=y)

    def tuple(self):
        return self.x, self.y

    @property
    def X(self):
        return self.x

    @property
    def Y(self):
        return self.y

    def __str__(self):
        return '({0.x}, {0.y})'.format(self)

    def get_rect(self, size):
        return Rect(self, Point(self.X + size.W, self.Y + size.H))


@auto_representer
class Size(Base):
    w = None
    h = None

    def __init__(self, w, h):
        if w is None:
            raise ValueError('w is None')
        if h is None:
            raise ValueError('h is None')
        Base.__init__(self, w=w, h=h)

    def tuple(self):
        return self.w, self.h

    @property
    def W(self):
        return self.w

    @property
    def H(self):
        return self.h

    @property
    def width(self):
        return self.w

    @property
    def height(self):
        return self.h

    def walk(self):
        for y in range(self.h):
            for x in range(self.w):
                yield Point(x, y)

    def __str__(self):
        return '({0.w}, {0.h})'.format(self)


# TODO: Implement
@auto_representer
class Polygon(Base):
    pass


@auto_representer
class Rect(Polygon):
    topleft = None
    topright = None
    bottomright = None
    bottomleft = None

    def __init__(self, topleft, topright, bottomright=None, bottomleft=None):
        """
        Rect(Point, Point, Point, Point)
        Rect(Point, Point)

        :param Point topleft:
        :param Point topright:
        :param Point|None bottomright:
        :param Point|None bottomleft:
        """
        if bottomright is None and bottomleft is None:
            bottomright = topright
            topright = Point(bottomright.x, topleft.y)
            bottomleft = Point(topleft.x, bottomright.y)

        width = topright.x - topleft.x
        height = bottomleft.y - topleft.y

        self.topleft = topleft
        self.topright = topright
        self.bottomright = bottomright
        self.bottomleft = bottomleft

        super(Rect, self).__init__(*topleft, width, height)

    @property
    def xw(self):
        return self.topright.x

    @property
    def yh(self):
        return self.bottomleft.y

    @property
    def center(self):
        return Point(self.x + self.w / 2, self.y + self.h / 2)

    @property
    def corner(self):
        return self.bottomright

    @property
    def width(self):
        return abs(self.topleft.x - self.topright.x)

    @property
    def height(self):
        return abs(self.topleft.y - self.bottomleft.y)

    @property
    def size(self):
        return Size(self.width, self.height)

    def tuple(self):
        return self.topleft, self.topright, self.bottomright, self.bottomleft

    def flat(self):
        for p in self.tuple():
            yield p.tuple()

    def walk(self):
        for x in range(self.width):
            for y in range(self.height):
                yield Point(x, y)


# TODO: Implement
@auto_representer
class Box(Rect):
    pass
