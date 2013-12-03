from __future__ import unicode_literals
from copy import copy
import hashlib
from django.core.cache import cache as cache_backend


class CachedFunction(object):
    """
    This class provides a simple API for caching and retrieving transparently
    the result of a call using Django's cache, as well as (re)setting and
    deleting the cached value.

    Example::

        class Foo(object):
            @cached_function(key='bar_{1}')
            def bar(self, x):
                print('Computing bar(%s)..' % x)
                return x*x

        >>> foo = Foo()
        >>> foo.bar(4)
        Computing bar(4)..
        16
        >>> foo.bar(4)              # result is now cached
        16
        >>> foo.bar.delete_cache(4) # delete the cache for this param
        >>> foo.bar(4)              # recompute (and cache) it
        Computing bar(4)..
        16
    """

    def __init__(self, fn, key=None, id=None, timeout=None, cache=True, memoize=True, hash_algorithm=hashlib.md5):
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
        self._fn = fn
        self._key = key
        self._id = id
        self._timeout = timeout
        self._cache = cache
        self._memoize = memoize
        self._hash_algorithm = hash_algorithm

        self._obj = None  # for bound methods' im_self object
        self._cached_results = {}

        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

        if key:
            if callable(key):
                self._key = key
            elif isinstance(key, basestring):
                self._key = str(key).format
            else:
                raise TypeError('%s keys are invalid' % key.__class__.__name__)
        else:
            def generate_key(*args, **kwargs):
                """
                Generates the cache key based on ``fn.__module__``, ``fn.__name__``.
                Also it includes class name (if any) and specified id (if any).

                :returns: formatted string
                :rtype: str or unicode
                """
                parts = []

                parts.append(fn.__module__)

                if hasattr(fn, '__self__'):
                    parts.append(fn.__self__.__class__.__name__)

                parts.append(fn.__name__)

                if id:
                    if callable(id):
                        _id = id
                    elif isinstance(id, basestring):
                        _id = str(id).format
                    else:
                        raise TypeError('%s keys are invalid' % id.__class__.__name__)

                    parts.append(_id(*args, **kwargs))

                ## TODO Implement args hashing
                #if args:
                #    parts.append(pickle.dumps(args))
                #
                #if kwargs:
                #    parts.append(pickle.dumps(sorted(kwargs.items())))

                return '.'.join(parts)

            self._key = generate_key

    def __call__(self, *args, **kwargs):
        """
        Returns the cached result of ``fn(*args, **kwargs)`` or computes and
        caches it if it's not already cached.

        This method alone covers the majority of use cases, allowing clients to
        use ``CachedFunction`` instances as plain callables.

        :returns: The cached or computed result.
        """
        key = None
        value = None
        memoization_key = None

        if self._memoize:
            memoization_key = self._get_memoization_key(*args, **kwargs)
            if memoization_key in self._cached_results:
                return self._cached_results[memoization_key]

        if self._cache:
            key = self.get_cache_key(*args, **kwargs)
            value = cache_backend.get(key)

        if value is None:
            value = self._fn(*self._inject_obj(args), **kwargs)

            if self._cache:
                cache_backend.set(key, value, timeout=self._timeout)

            if self._memoize:
                self._cached_results[memoization_key] = value

        return value

    def reset_cache(self, *args, **kwargs):
        """"
        Computes ``fn(*args, **kwargs)`` and stores it in the cache.

        Unlike :meth:`__call__`, this method sets the cache unconditionally,
        without checking first if a key corresponding to a call with the same
        parameters already exists.

        :returns: The newly computed (and cached) result.
        """
        value = self._fn(*self._inject_obj(args), **kwargs)

        if self._cache:
            key = self.get_cache_key(*args, **kwargs)
            cache_backend.set(key, value, timeout=self._timeout)

        if self._memoize:
            memoization_key = self._get_memoization_key(*args, **kwargs)
            self._cached_results[memoization_key] = value

        return value

    def delete_cache(self, *args, **kwargs):
        """
        Deletes the cached and memoized result (if any) corresponding to a call
        with ``args`` and ``kwargs``.
        """
        if self._cache:
            key = self.get_cache_key(*args, **kwargs)
            cache_backend.delete(key)

        if self._memoize:
            memoization_key = self._get_memoization_key(*args, **kwargs)
            if memoization_key in self._cached_results:
                del self._cached_results[memoization_key]

    def get_cache_key(self, *args, **kwargs):
        """
        Returns the cache key corresponding to a call with ``args`` and ``kwargs``.

        This is mainly for debugging and for interfacing with external services;
        clients of this class normally don't need to deal with cache keys explicitly.
        """
        key = self._key(*self._inject_obj(args), **kwargs)

        if self._hash_algorithm:
            key = self._hash_algorithm(key).hexdigest()

        return key

    def _get_memoization_key(self, *args, **kwargs):
        """
        Returns the memoization key corresponding to a call with ``args`` and ``kwargs``.
        """
        #result = [id(fn)]
        #for arg in args:
        #    result.append(id(arg))
        #result.append(id(mark))
        #for key, value in kwargs:
        #    result.append(key)
        #    result.append(id(value))
        #return tuple(result)
        key = str(self._inject_obj(args)) + str(kwargs)
        return key

    def _inject_obj(self, args):
        if self._obj is not None:
            return (self._obj,) + args
        return args

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        new = copy(self)
        new._obj = obj
        return new


def cached_function(*args, **kwargs):
    if args:  # @cached_property
        return CachedFunction(args[0])
    else:     # @cached_property(key=...)
        return lambda fn: CachedFunction(fn, **kwargs)
