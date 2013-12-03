from __future__ import unicode_literals
from django.test import TestCase
from cached_result.decorators import cached_property


class CachedFunctionTest(TestCase):
    def test_property(self):
        class A(object):
            def __init__(self, name):
                self._name = name
                self.hits_count = 0

            @cached_property
            def name(self):
                self.hits_count += 1
                return self._name

            @name.setter
            def name(self, value):
                self._name = value

            @name.deleter
            def name(self):
                del self._name

            @cached_property
            def read_only(self):
                self.hits_count += 1
                return 'baz'

        # test type
        self.assertIsInstance(A.name, property)
        from cached_result.decorators.cached_property import CachedProperty
        self.assertIsInstance(A.name, CachedProperty)

        obj = A('foo')

        # test getter
        self.assertEqual(obj.hits_count, 0)
        self.assertEqual(obj.name, 'foo')
        self.assertEqual(obj.hits_count, 1)
        self.assertEqual(obj.name, 'foo')
        self.assertEqual(obj.hits_count, 1)

        # test setter
        obj.name = 'bar'
        self.assertEqual(obj.name, 'bar')
        self.assertEqual(obj.hits_count, 2)

        # test deleter
        del obj.name
        self.assertRaises(AttributeError, lambda: obj.name)

        # test setter again
        obj.name = 'foobar'
        self.assertEqual(obj.name, 'foobar')
        self.assertEqual(obj.hits_count, 4)

        # test the read-only property
        self.assertEqual(obj.read_only, 'baz')
        self.assertEqual(obj.hits_count, 5)
        self.assertEqual(obj.read_only, 'baz')
        self.assertEqual(obj.hits_count, 5)

        # test modifying a read-only property
        def set_read_only():
            obj.read_only = 'foo'

        self.assertRaises(AttributeError, set_read_only)

        def del_read_only():
            del obj.read_only

        self.assertRaises(AttributeError, del_read_only)