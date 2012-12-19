# -*- encoding: utf-8 -*-
'''
    libpip2pi
    ~~~~~~~~~

    A library to build a PyPI-compatible package repository from pip
    requirements.

    :copyright: (c) 2012 by David Wolever.
    :license: BSD, see LICENSE for more details.
'''

from .parser import get_parser

__version__ = (0, 1, 5)


def main():
    args = get_parser().parse_args()

