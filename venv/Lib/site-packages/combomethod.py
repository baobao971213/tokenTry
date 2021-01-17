"""
Decorator that allows a method to be both a class method
and an instance method at the same time.
"""

# Yet again I am indebted to Stack Overflow
# http://stackoverflow.com/questions/2589690/creating-a-method-that-is-simultaneously-an-instance-and-class-method

import functools


class combomethod(object):
    """
    A combomethod is a method that can be called as either a classmethod
    or an intstance method. The "receiver" of the message is akin to
    traditional ``self`` and ``cls`` parameters, but can be either.

    For example::

        class A(object):

            @combomethod
            def either(receiver, x, y):
                return x + y

    Can now be called as either:"

        A.either(1, 3)

    Or::

        a = A()
        a.either(1, 3)

    """

    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)
        return _wrapper
