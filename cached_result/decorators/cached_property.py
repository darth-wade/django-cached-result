from __future__ import unicode_literals
import hashlib
from cached_result.decorators.cached_function import CachedFunction


class CachedProperty(property, CachedFunction):
    """
    This class provides a simple API for caching and retrieving transparently
    the result of a property using Django's cache, as well as (re)setting and
    deleting the cached value.

    Example::

        class Foo(object):
            @cached_property(key='bar_{0}')
            def bar(self):
                print('Computing bar()..')
                return 42

        >>> foo = Foo()
        >>> foo.bar
        Computing bar()..
        42
        >>> foo.bar  # result is now cached
        42
        >>> Foo.bar.delete_cache(foo)  # API are available through the class
        >>> foo.bar
        Computing bar()..
        42
    """

    def __init__(self, fn, key=None, id=None, timeout=None, cache=True, memoize=True, hash_algorithm=hashlib.md5,
                 fset=None, fdel=None, doc=None):
        """
        Initializes a wrapper of ``fn``.

        :param fn: The callable to be wrapped. It may take any number of
            positional and/or keywords arguments.
        :param key: Specifies how to determine the cache key for a given
            ``fn(*args, **kwargs)`` call; it can be:

            - A callable: The cache key is computed as ``key(*args, **kwargs)``.
              Obviously ``key`` must have the same (or compatible) signature
              with ``fn``.
            - A string: A format string. The cache key is
              determined as ``key.format(*args, **kwargs)``.
        :param id: Additional identifier for generated key; it can be:

            - A callable: The cache key is computed as ``key(*args, **kwargs)``.
              Obviously ``key`` must have the same (or compatible) signature
              with ``fn``.
            - A string: A format string. The cache key is
              determined as ``key.format(*args, **kwargs)``.
        :param timeout: If given, that timeout will be used for the key;
            otherwise the default cache timeout will be used.
        :param cache: Specifies whether the cache used
        :param memoize: Specifies whether the memoization used
        :param hash_algorithm: Specifies the hash algorithm for
            cache key or None if do nothing
        """
        self._fset = fset
        self._fdel = fdel

        self.__doc__ = doc or getattr(fn, '__doc__', None)

        CachedFunction.__init__(self, fn, key=key, id=id, timeout=timeout, cache=cache, memoize=memoize,
                                hash_algorithm=hash_algorithm)

        property.__init__(self, fget=self.__call__, fset=fset, fdel=fdel)

    def setter(self, fset):
        self._fset = fset
        return self

    def deleter(self, fdel):
        self._fdel = fdel
        return self

    def __set__(self, obj, value):
        if self._fset is None:
            raise AttributeError('Can\'t set attribute')
        self._fset(obj, value)
        self.delete_cache(obj)

    def __delete__(self, obj):
        if self._fdel is None:
            raise AttributeError('Can\'t delete attribute')
        self._fdel(obj)
        self.delete_cache(obj)


def cached_property(*args, **kwargs):
    if args:  # @cached_property
        return CachedProperty(args[0])
    else:     # @cached_property(key=...)
        return lambda fn: CachedProperty(fn, **kwargs)
