"""
Note on this implementation: I originally inherited directly from frozenset. 
But for some reason, this resulted in not being able to create an Enum
by calling Enum(arg1, arg2, arg3), only Enum([arg1, arg2])
So I deliberatly decided to make it more complicated (need for a __initialized
attribute and checks on this attribute) in order to have nicer instanciation.
"""
class Enum(object):
    """
    Enum class to be used like that:
    MyEnum = Enum("NAME1", "NAME2", "NAME3", X, Y, Z)
    """
    __values = None
    __initialized = False

    def __init__(self, *arg):
        self.__values = frozenset(arg)
        self.__initialized = True

    def __getattr__(self, name):
        if self.__initialized is True:
            if name in self.__values:
                return name
        else:
            return self.__initialized
        raise AttributeError

    def __setattr__(self, attr, val):
        if self.__initialized is False:
            # Somehow, you can get an attribute by accessing self.attribute inside __getattr__
            # but you can set an attribute using self.attribute = sthing, inside __setattr__
            # So, well, just use the intrinsic dict
            self.__dict__[attr] = val
        else:
            raise BaseException("Enums are immutable")

    def __delattr__(self, attr):
        raise BaseException("Enums are immutable")

    def __iter__(self):
        return self.__values.__iter__()