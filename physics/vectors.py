import numpy as np

class vector(object):
    def __init__(self, input_var):
        if type(input_var) == vector:
            self.x = input_var.x
            self.y = input_var.y
        elif type(input_var) == tuple:
            self.x = input_var[0]
            self.y = input_var[1]
        else:
            raise ValueError("Couldn't convert {!s} to vector.".format(type(input_var)))
                             
    def __repr__(self):
        return "X: {:.3E}\nY: {:.3E}".format(self.x, self.y)
    def __add__(self, other):
        return vector((self.x + other.x, self.y + other.y))
    def __sub__(self, other):
        return vector((self.x - other.x, self.y - other.y))
    def __mul__(self, other):
        if type(other) == vector:
            raise ValueError("Can only multiply a vector by a scalar.")
        coeff = float(other)
        return vector((self.x*coeff, self.y*coeff))
    def __truediv__(self, other):
        if type(other) == vector:
            raise ValueError("Can only multiply a vector by a scalar.")
        coeff = float(other)
        return vector((self.x/coeff, self.y/coeff))
    
    @property
    def magnitude(self):
        return np.sqrt(np.square(self.x) + np.square(self.y))
    
    @property
    def direction(self):
        if self.x >= 0 and self.y >= 0:
            return np.arctan(np.abs(self.y) / np.abs(self.x))
        elif self.x < 0 and self.y >= 0:
            return np.pi - np.arctan(np.abs(self.y) / np.abs(self.x))
        elif self.x < 0 and self.y < 0:
            return np.pi + np.arctan(np.abs(self.y) / np.abs(self.x))
        else:
            return 2*np.pi - np.arctan(np.abs(self.y) / np.abs(self.x))
    
def vector_dot(vector1, vector2):
    """Returns an inner (dot) product of two vectors.
    """
    return float(vector1.x*vector2.x + vector1.y*vector2.y)

def vector_cross(vector1, vector2):
    raise NotImplemented
    # This one not yet implemented because I'm working in a 2D coordinate space for the time being.
    