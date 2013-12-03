Django Cached Result
====================
.. image:: https://secure.travis-ci.org/darth-wade/django-cached-result.png?branch=master
   :target: https://travis-ci.org/darth-wade/django-cached-result

Simple API for quick and transparent caching/memoization of functions or dynamic properties results.

.. code-block:: python

    class Foo(object):
        @cached_function(key='bar_{1}')
        def bar(self, x):
            print('Computing bar(%s)..' % x)
            return x*x

        @cached_property
        def baz(self):
            print('Computing baz()..')
            return 42

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

    >>> foo.baz
    Computing baz()..
    42
    >>> foo.baz  # result is now cached
    42
    >>> Foo.baz.delete_cache(foo)  # API are available through the class
    >>> foo.baz
    Computing baz()..
    42


Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-cached-result

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/darth-wade/django-cached-result.git#egg=cached_result

Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-cached-result
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
