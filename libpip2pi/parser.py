# -*- encoding: utf-8 -*-
'''
    libpip2pi.parser
    ~~~~~~~~~~~~~~~~

    A simple class that implements a command line parser for pip2pi.

    :copyright: (c) 2012 by David Wolever.
    :license: BSD, see LICENSE for more details.
'''


import argparse


def get_parser():
    '''
    instantiates a parser.
    '''
    parser = argparse.ArgumentParser(description='Build a PyPI-compatible '
                                     'package repository from pip '
                                     'requirements.')

    parser.add_argument('-o', '--output', nargs=1, metavar='<DIR>',
                        help='Create repository in <DIR> (default: current '
                        'directory)')

    parser.add_argument('-b', '--build', nargs=1, metavar='<DIR>',
                        help='Temporary directory to build the repository.'
                        'This directory will be deleted at the end.'
                        '(default: /tmp/pip2pi)')

    parser.add_argument('-r', '--requirements', nargs='*', metavar='<FILENAME>',
                        help='Mirror all the packages listed in the given'
                        'requirements file. This option can by used multiple'
                        'times.')

    parser.add_argument('package', metavar='PACKAGE_NAMES', nargs='*',
                        help='a package name (and version) in pip format.')

    return parser
