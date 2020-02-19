#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")

try:
    long_description = open("README.rst", "U").read()
except IOError:
    long_description = "See https://github.com/wolever/pip2pi"

import pip2pi
version = ".".join(map(str, pip2pi.__version__))

setup(
    name="pip2pi",
    version=version,
    url="https://github.com/wolever/pip2pi",
    author="David Wolever",
    author_email="david@wolever.net",
    description="pip2pi builds a PyPI-compatible package repository from pip requirements",
    long_description=long_description,
    maintainer="Md Safiyat Reza",
    maintainer_email="safiyat@voereir.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dir2pi = pip2pi.commands:dir2pi',
            'pip2pi = pip2pi.commands:pip2pi',
            'pip2tgz = pip2pi.commands:pip2tgz',
        ],
    },
    install_requires=[
        "pip>=1.1",
    ],
    license="BSD",
    classifiers=[ x.strip() for x in """
        Development Status :: 4 - Beta
        Environment :: Console
        Intended Audience :: Developers
        Intended Audience :: System Administrators
        License :: OSI Approved :: BSD License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Topic :: Software Development
        Topic :: Utilities
    """.split("\n") if x.strip() ],
)
