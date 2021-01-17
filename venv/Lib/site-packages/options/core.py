"""Options"""

import sys
from copy import copy

from combomethod import combomethod
from nulltype import NullType

# from collections import OrderedDict  #, chainstuf
# temporarily pulled stuf version of chainstuf in favor of
# local version until a bug with generator values can be
# tracked down and fixed
from .chainstuf import chainstuf
from .config import read_dict, write_dict
from .funclike import *

# Sentinels
Unset      = NullType('Unset')
Prohibited = NullType('Prohibited')
Transient  = NullType('Transient')
Reserved   = NullType('Reserved')


def bad_option_name(name):
    return hasattr(Options, name)


class BadOptionName(AttributeError):
    """
    Raised when an Options object is given an option name that conflicts
    with an existing method.
    """
    pass


def attrs(m, first=[], underscores=False):
    """
    Given a mapping m, return a string listing its values in a
    key=value format. Items with underscores are, by default, not
    listed. If you want some things listed first, include them in
    the list first.
    """
    keys = first[:]
    for k in m.keys():
        if not underscores and k.startswith('_'):
            continue
        if k not in first:
            keys.append(k)
    return ', '.join(["{0}={1}".format(k, repr(m[k])) for k in keys])


class Options(chainstuf):

    """
    Options handler.
    """

    def __init__(self, **kwargs):
        """
        Create an Options object. Its initial values are set via kwargs.
        No "magical processing" is done for this intialaliation.
        """
        super(Options, self).__init__()
        # top = OrderedDict()
        top = dict()
        self.maps[0] = top
        for k, v in kwargs.items():
            if bad_option_name(k):
                raise BadOptionName("Options already defines an attribute {0!r}".format(k))
            else:
                top[k] = v
        self._magic = {}


    def _magicalized(self, key, value):
        """
        Get the magically processed value for a single key value pair.
        If there is no magical processing to be done, just returns value.
        """
        magicfn = self._magic.get(key, None)
        if magicfn is None:
            return value
        argcount = func_code(magicfn).co_argcount
        if argcount == 1:
            return magicfn(value)
        elif argcount == 2:
            return magicfn(value, self)
        elif argcount == 3:
            return magicfn(None, value, self)
        else:
            msg = 'magic functions take 1-3 arguments, not {0}'.format(argcount)
            raise ValueError(msg)


    def _process(self, kwargs):
        """
        Given kwargs, removes any key=value pairs corresponding to this set of
        options. Those pairs are interpreted according to 'paramater
        interpretation magic' if needed, then returned as dict. Any key:value
        pairs remaining in kwargs are not options related to this class, and may
        be used for other purposes.
        """
        opts = {}
        for key, value in kwargs.items():
            if key in self:
                opts[key] = self._magicalized(key, value)

        # delete 'taken' options from kwargs
        for key in opts:
            del kwargs[key]

        return opts


    def set(self, **kwargs):
        """
        Set is a type of update. It takes only kwargs, and it pchecks each
        one individually, interpreting sentienels such as ``Prohibited`` and
        magically processing items.
        """
        newopts = self._process(kwargs)
        for k, v in newopts.items():
            if self[k] is Prohibited:
                raise KeyError("changes to '{0}' are prohibited".format(k))
            elif v is Unset:
                del self.maps[0][k]
            else:
                self.maps[0][k] = v

        # should this return self for fluid style of calling?


    def setdefault(self, key, default):
        """
        If key is in the dictionary, return its value. If not, insert key with a
        value of default and return default. If the value is Prohibited, no
        change will be allowed, and a KeyError will be raised. If the value is
        Transient or Unset, it will be as if the value were never there, and the
        default will be set. NB ``setdefault`` does not participate in "magical"
        value interpretation.
        """
        try:
            value = self[key]
            if value is Prohibited:
                raise KeyError("changes to {0!r} are prohibited".format(key))
            elif value is Transient or value is Unset:
                self[key] = default
                return default
            else:
                return value
        except KeyError as e:
            # All keys must be defined in initial object construction,
            # even if defined as Unset or Transient. So if *no* value
            # is available for a key, definite error. Stricter than
            # general dict / mapping practice.
            raise e
            # check this wrt new strategy

        # In general usage, ``setdefault`` will be called only on ``OptionsChain``
        # instances, but defined for ``Options`` as well for completeness.


    def update(self, *args, **kwargs):
        """
        Update self with the given data. Necessary to avoid apparent bug in
        ``stuf`` when updating with iterable objects, especially generators. NB
        ``update`` does not participate in "magical" value interpretation.
        """
        itemize = lambda a: a if isinstance(a, list) else a.items()
        for a in args:
            for k, v in itemize(a):
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

        # Is this really necessary, given new leaner foundation?


    def new_child(self):

        child = self.__class__()
        child.maps = self.maps[:]  # NB shallow copy of list
        child.maps.insert(0, {})
        return child


    def copy(self):
        """
        New Options with a new copy of maps[0] and refs to maps[1:]
        """
        result = self.__class__()
        result.maps = self.maps[1:]
        result.maps.insert(0, self.maps[0].copy())
            # NB copy of first item, refs to later ones
            # based on Python 3.5 ChainMap semantics
        return result

    __copy__ = copy


    def push(self, kwargs):
        """
        Create the next layer down.
        """
        layer = self.new_child()
        # find kwargs to be used in setting the new layer
        useargs = {}
        for k, v in kwargs.items():
            if k in self:
                useargs[k] = v
        layer.set(**useargs)

        # remove args that were used in setting
        for k in useargs:
            del kwargs[k]
        return layer


    # def __iter__(self):
    #    for k in super(Options, self).keys():
    #        if not k.startswith('_'):
    #            yield k
    #    raise StopIteration


    def items(self):
        """
        Return items of self, but none that are 'internal' (ie start with underscore _)
        """
        return [(k, v) for (k, v) in super(Options, self).items() if not k.startswith('_')]

        # should this "only external values" behavior be mapped to keys and values
        # methods as well?

    def add(self, **kwargs):
        """
        Create the next layer down. Like ``push()``, but accepts full kwargs
        not just a dict. Typical use would be for subclasses, called as part
        to define their
        own class options, rather than for instances to call.
        """
        child = self.new_child()
        for key, value in kwargs.items():
            if bad_option_name(key):
                raise BadOptionName("Options already defines an attribute {0!r}".format(key))
            else:
                child[key] = value
        return child


    def addflat(self, args, keys):
        """
        Sometimes kwargs aren't the most elegant way to provide options. In those
        cases, this routine helps map flat args to kwargs. Provide the actual args,
        followed by keys in the order in which they should be consumed. There can
        be more keys than args, but not the other way around. Returns a list of
        keys used (from which one can also determine if a key was not used).
        """
        if not args:
            return []
        if len(args) > len(keys):
            raise ValueError('More args than keys not allowed')
        additional = dict(zip(keys, args))
        self.update(additional)
        keys_used = list(additional.keys())
        return keys_used

        # Shouldn't the update line involve a set for magicalization?

    def magic(self, **kwargs):
        """
        Set some options as having 'magical' update properties. In a sense, this
        is like Python ``properties`` that have a setter.  NB no magical
        processing is done to the base Options. These are assumed to have whatever
        adjustments are needed when they are originally set.
        """
        self.setdefault('_magic', {})
        for k, v in kwargs.items():
            self._magic[k] = real_func(v)

    def magical(self, key):
        """
        Instance based decorator, specifying a function in the using module
        as a magical function. Note that the magical methods will be called
        with a self of None.
        """
        def my_decorator(func):
            self._magic[key] = func
            return func

        return my_decorator

    def write(self, filepath, encoding='utf-8'):
        """
        Save configuration values to the given filepath.

        :param str filepath: Path to write values to
        :param str encoding: Encoding of Unicode to use
        """
        write_dict(dict(self), filepath, encoding)

    @classmethod
    def read(cls, filepath, encoding='utf-8'):
        """
        Load configuration values from the given filepath.
        Note this is a classmethod, invoked ``Options.read(...)``
        while ``write`` is specific to an instance, and invoked
        ``opts.write(...)``.

        :param str filepath: Path to read values from
        :param str encoding: Encoding of Unicode to use
        :returns: resulting Options object
        :rtype: Options
        """
        d = read_dict(filepath, encoding)
        return cls(**d)

    def __eq__(self, other):
        skeys = sorted(self.keys())
        if skeys != sorted(other.keys()):
            return False
        for k in skeys:
            if k == '_magic':
                continue
            if self[k] != other[k]:
                return False
        return True

    def __repr__(self):
        clsname = self.__class__.__name__
        # return "{0}({1!r})".format(clsname, self.maps)
        return "{0}({1})".format(clsname, attrs(self))


class OptionsClass(object):

    """
    Class from which client classes can inherit. It inherently supports
    add ``set`` and ``settings`` methods.
    """

    options = Options()

    @combomethod
    def set(receiver, **kwargs):
        """
        Change the receiver's settings to those defined in the kwargs.
        An update-like function. This uplevels calls that would look
        like ``Class.options.set(...)`` to the simpler ``Class.set(...)``.
        Works on either class or instance receivers. Requires that one
        uses the instance variable ``options`` to store persistent
        configuration data.
        """
        receiver.options.set(**kwargs)

    def settings(self, **kwargs):
        """
        Open a context manager for a `with` statement. Temporarily change settings
        for the duration of the with.
        """
        return OptionsContext(self, kwargs)

    def __repr__(self):
        clsname = self.__class__.__name__
        return "{0}({1})".format(clsname, attrs(self.options))


class OptionsContext(object):

    """
    Context manager so that modules that use Options can easily implement
    a `with x.settings(...):` capability. In x's class:

    def settings(self, **kwargs):
        return OptionsContext(self, kwargs)
    """

    def __init__(self, caller, kwargs):
        """
        When `with x.method(*args, **kwargs)` is called, it creates an OptionsContext
        passing in its **kwargs.
        """
        self.caller = caller
        if 'opts' in kwargs:
            kwargs.update(kwargs['opts'])
            del kwargs['opts']

        caller.options = caller.options.push(kwargs)

    def __enter__(self):
        """
        Called when the `with` is about to be 'entered'. Whatever this returns
        will be the value of `x` if the `as x` construction is used. Not generally
        needed for option setting, but might be needed in a subclass.
        """
        return self.caller

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when leaving the `with`. Reset caller's options to what they were
        before we entered.
        """
        self.caller.options.maps.pop(0)
