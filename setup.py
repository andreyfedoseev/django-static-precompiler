from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import re
import sys


if sys.version_info.major == 2:
    install_requires = [
        "Django>=1.7,<2.0",
        "typing",
    ]
elif sys.version_info.major == 3:
    install_requires = [
        "Django>=1.9",
    ]
else:
    raise AssertionError()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    if sys.version < '3':
        return open(path).read()
    return open(path, encoding="utf-8").read()


README = read('README.rst')
CHANGES = read('CHANGES.rst')


version = ""

with open("static_precompiler/__init__.py") as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


setup(
    name="django-static-precompiler",
    packages=find_packages(),
    version=version,
    author="Andrey Fedoseev",
    author_email="andrey.fedoseev@gmail.com",
    url="https://github.com/andreyfedoseev/django-static-precompiler",
    description="Django template tags to compile all kinds of static files "
                "(SASS, LESS, Stylus, CoffeeScript, Babel, LiveScript, Handlebars).",
    long_description="\n\n".join([README, CHANGES]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=["sass", "scss", "less", "stylus", "css", "coffeescript", "javascript", "babel", "livescript",
              "handlebars"],
    install_requires=install_requires,
    tests_require=[
        "pytest",
        "pytest-django",
        "pretend",
        "libsass",
    ],
    extras_require={
        'watch': ['watchdog'],
        'libsass': ['libsass']
    },
    cmdclass={
        "test": PyTest
    },
)
