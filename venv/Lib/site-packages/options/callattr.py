"""
Helper functions to set attribtues on a callable
object (function, method, callable instance, or
lambda).
"""
import sys
_PY2 = sys.version_info[0] == 2

if _PY2:
    class _ALFKJSLJD(object):
        def m(self): pass

    meth_type = type(_ALFKJSLJD.m)


def callable_func(target):
    if _PY2 and isinstance(target, meth_type):
        return target.__func__
    return target


def callable_setattr(target, name, value):
    setattr(callable_func(target), name, value)


def callable_getattr(target, name):
    try:
        return getattr(callable_func(target), name)
    except AttributeError:
        return None


def callable_hasattr(target, name):
    return hasattr(callable_func(target), name)

