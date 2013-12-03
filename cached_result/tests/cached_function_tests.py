from __future__ import unicode_literals
from time import sleep
from django.test import TestCase
from django.core.cache import cache
from cached_result.decorators import cached_function


class CachedFunctionTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_name_and_doc(self):
        @cached_function
        def a():
            """sample doc"""
            return 1

        self.assertEqual(a.__name__, 'a')
        self.assertEqual(a.__doc__, 'sample doc')

        class B:
            @cached_function
            def b(self, id=None):
                """second doc"""
                return id

        b = B()

        self.assertEqual(b.b.__name__, 'b')
        self.assertEqual(b.b.__doc__, 'second doc')

    def test_identifier(self):
        class A:
            def __init__(self, name):
                self._name = name
                self.hits_count = 0

            @cached_function(id='{0._name}', hash_algorithm=None)
            def name(self):
                """sample doc"""
                self.hits_count += 1
                return self._name

        a = A('Wade')

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 1)

        a.name.delete_cache()
        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 2)

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 2)

    def test_identifier_uniqueness(self):
        hits = []

        @cached_function(id='{0}')
        def func(value):
            hits.append(1)
            return value * 2

        self.assertEqual(func(1), 2)
        self.assertEqual(len(hits), 1)

        self.assertEqual(func(2), 4)
        self.assertEqual(len(hits), 2)

        func.delete_cache(1)
        self.assertEqual(func(1), 2)
        self.assertEqual(len(hits), 3)

        self.assertEqual(func(3), 6)
        self.assertEqual(len(hits), 4)

        self.assertEqual(func(1), 2)
        self.assertEqual(len(hits), 4)

        self.assertEqual(func(2), 4)
        self.assertEqual(len(hits), 4)

    def test_key(self):
        class A:
            def __init__(self, name):
                self._name = name
                self.hits_count = 0

            @cached_function(key='test-key-{0._name}', hash_algorithm=None)
            def name(self):
                """sample doc"""
                self.hits_count += 1
                return self._name

        a = A('Wade')

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 1)

        key = a.name.get_cache_key()
        self.assertEqual(key, 'test-key-%s' % a.name())
        self.assertIsNotNone(cache.get(key))
        self.assertEqual(cache.get(key), 'Wade')

        a.name.delete_cache()
        self.assertIsNone(cache.get(key))

    def test_timeout(self):
        class A:
            def __init__(self, name):
                self._name = name
                self.hits_count = 0

            @cached_function(timeout=0.1, memoize=False)  # 100 ms
            def name(self):
                """sample doc"""
                self.hits_count += 1
                return self._name

        a = A('Wade')

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 1)

        sleep(0.15)

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 2)

    def test_memoization(self):
        hits = []

        @cached_function(cache=False)
        def func(value):
            hits.append(1)
            return value * 2

        self.assertEqual(func(1), 2)
        self.assertEqual(len(hits), 1)
        self.assertIsNone(cache.get(func.get_cache_key(1)))

        self.assertEqual(func(2), 4)
        self.assertEqual(len(hits), 2)

        func.delete_cache(1)
        self.assertEqual(func(1), 2)
        self.assertEqual(len(hits), 3)

        self.assertEqual(func(3), 6)
        self.assertEqual(len(hits), 4)

        self.assertEqual(func(1), 2)
        self.assertEqual(len(hits), 4)

        self.assertEqual(func(2), 4)
        self.assertEqual(len(hits), 4)

    def test_reset(self):
        class A:
            def __init__(self, name):
                self._name = name
                self.hits_count = 0

            @cached_function(key='test-key-{0._name}', hash_algorithm=None)
            def name(self):
                """sample doc"""
                self.hits_count += 1
                return self._name

        a = A('Wade')

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 1)

        a.name.reset_cache()

        self.assertEqual(a.name(), 'Wade')
        self.assertEqual(a.hits_count, 2)