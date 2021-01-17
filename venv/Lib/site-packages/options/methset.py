import sys

"""
Support functions for method- and function-specific
setting.
"""

# FIXME: Currenlty depends on class-level meth_defaults dict
# which doesnt apply to functions, and is coarse. Switch instead
# to __kwargs__

_PY3 = sys.version_info[0] > 2

def method_push(base_options, kwdefaults, kwargs):
    """
    Transitional helper function to simplify the grabbing of
    method-specific arguments. Evolved from first-gen approach.
    Still evolving.
    """
    mkwargs = kwdefaults.copy()
    mkwargs.update(kwargs)
    if base_options:
        answer = base_options.push(mkwargs)
        answer.update(mkwargs) # add everything else, for subclasses
                               # probably needs to be a pushall option for this use case
        return answer
    else:
        return mkwargs


def enable_func_set(entry, cls=None):
    """
    :param entry: The method or function to be made settable.
    :para cls: Optional class. Required if target is a method or method name.
    """
    if cls is None:
        raise NotImplementedError
    func = entry if _PY3 or not hasattr(entry, '__func__') else entry.__func__
    if not hasattr(func, '__kwdefaults__'):
        setattr(func, '__kwdefaults__', {})
    elif getattr(func, '__kwdefaults__') is None:
        setattr(func, '__kwdefaults__', {})

    setattr(func, 'set', lambda **kwargs: func.__kwdefaults__.update(kwargs))


# Decorator-based enablement as way to get around limits on
# introspection and reduce code compleixty. Inspired by:
# http://stackoverflow.com/a/2367605/240490

METH_FLAG = "method_settable"

def enable_method_set(cls):
    """
    Decorator based ennoblement.
    """
    for name, method in cls.__dict__.items():
        # print(name, method, cls, type(method))
        if callable(method) and hasattr(method, METH_FLAG):
            enable_func_set(method, cls)
    return cls

def method_set(method):
    """
    Mark a method as something that requires enable_method_set
    to act upon.
    """
    setattr(method, METH_FLAG, True)
    return method

def method_set2(self, func, **dkwargs):
     """
     Show arguments to a function. Decorator itself may
     take arguments, or not. Whavevs.
     """

     # argument prep for decorator with optional arguments
     no_args = False
     if not dkwargs:
         # We were called without args
         no_args = True

     def method_set_decorator(func):

         def inner_func(*args, **kwargs):
             # update some options, in case they've changed in the meanwhile
             opts.update(self.inout.__kwdefaults__)
             opts.update(dkwargs)
             try:
                 retval = func(*args, **kwargs)
                 return retval
             except Exception as e:  # pragma: no cover
                 raise e

         return ommer_func

     if no_args:
         return method_set_decorator(func)
     else:
         return method_set_decorator
