from setuptools import setup, find_packages
import os
import sys


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    if sys.version < '3':
        return open(path).read()
    return open(path, encoding="utf-8").read()


README = read('README.rst')
CHANGES = read('CHANGES.rst')

setup(
    name="django-static-precompiler",
    packages=find_packages(),
    version="0.5.3",
    author="Andrey Fedoseev",
    author_email="andrey.fedoseev@gmail.com",
    url="https://github.com/andreyfedoseev/django-static-precompiler",
    description="Django template tags to compile all kinds of static files "
                "(SASS, LESS, CoffeeScript).",
    long_description="\n\n".join([README, CHANGES]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=["sass", "scss", "less", "css", "coffeescript", "javascript"],
    requires=[
        "six",
    ],
    tests_require=[
        "mock",
    ],
    test_suite="static_precompiler.tests.suite",
)
