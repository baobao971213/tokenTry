"""
Sidecar to add ``stuf``-like attribute access to ``ChainMap``. Does not use
``stuf`` directly, given an intstallability problem in recent releases that
precluded use on 2.6, as well as a bug as of 0.9.12 when using generators as
mapping values. This light shim over ``ChainMap`` has neither bug.
"""

from chainmap import ChainMap

class chainstuf(ChainMap):

    """
    A stuf-like surfacing of the ChainMap collection (multi-layer dict)
    introduced in Python 3. Uses a workalike replacement to make suitable
    for Python 2.6, Python 3.2, and PyPy3.
    """

    def __init__(self, *maps):
        ChainMap.__init__(self, *maps)

    def __getattr__(self, key):
        for m in self.maps:
            try:
                return m[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setattr__(self, key, value):
        if key == 'maps' or key in self.__dict__:
            ChainMap.__setattr__(self, key, value)
        else:
            self.maps[0][key] = value
