from __future__ import unicode_literals
import codecs
import os
from setuptools import setup, find_packages
import cached_result as app


dev_requires = [
    'flake8',
]

install_requires = [
    'django>=1.4,<1.7',
]


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


setup(
    name='django-cached-result',
    version=app.__version__,
    description='Simple API for quick and transparent caching of function or dynamic property results',
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, cache, memoize, cached function, cached property',
    author='Vadym Petrychenko',
    author_email='darth.wade@live.com',
    url='https://github.com/darth-wade/django-cached-result',
    download_url='https://pypi.python.org/pypi/django-cached-result',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
)
