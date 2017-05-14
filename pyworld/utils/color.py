from pyworld.utils import attrdict


class RGBA(attrdict.TupledAttrDict):
    R = 0
    G = 0
    B = 0
    A = 255

    def __init__(self, R=0, G=0, B=0, A=255, **kwargs):
        if not 0 <= R <= 255:
            raise ValueError('R: invalid value %s' % R)
        if not 0 <= G <= 255:
            raise ValueError('R: invalid value %s' % G)
        if not 0 <= B <= 255:
            raise ValueError('R: invalid value %s' % B)
        if not 0 <= A <= 255:
            raise ValueError('R: invalid value %s' % A)

        super(RGBA, self).__init__(R=int(R), G=int(G), B=int(B), A=int(A), **kwargs)

    def tuple(self):
        return self.R, self.G, self.B, self.A

    def __mul__(self, other):
        return RGBA(self.R * other, self.G * other, self.B * other)


white = lambda: RGBA(255, 255, 255)
black = lambda: RGBA(0, 0, 0)

red = lambda: RGBA(255, 0, 0)
green = lambda: RGBA(0, 255, 0)
blue = lambda: RGBA(0, 0, 255)

transparent = lambda: RGBA(0, 0, 0, 0)
