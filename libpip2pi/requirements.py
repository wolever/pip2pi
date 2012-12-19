# -*- encoding: utf-8 -*-
'''
    pip2pi.requirements
    ~~~~~~~~~~~~~~~~~~~

    Implements class and helper to list required packages for your private
    PyPI repository.
'''


class Requirements(object):
    '''
    is an iterable class providing a tuple (package, options) compatibles
    with pip arguments.
    '''

    def __init__(self):
        self._dict = {}

    def add_package(self, package, source=None, cache=False):
        '''
        add a package in the requirements list.

        :param package: the package name and its version options. For example
        package==1.4.5, package>=1.4 or package will work.

        :param source: the source for the package. This could be a pip
        download cache or a pypi compatible mirror.

        :param cache: set this to `True` if this is a pip download cache,
        `False` otherwise.
        '''
        self._dict[package] = None
        if source is not None and cache:
            self._dict[package] = "--download-cache=%s" % source
        elif source is not None:
            self._dict[package] = "--index-url=%s" % source

    def __iter__(self):
        return self._dict.iteritems()


def parse_file(requirements, source_file):
    '''
    A simple requirements.txt file parser appending packets to an existing
    Requirements object.
    '''
    required_list = open(source_file, 'r')
    for line in required_list:
        source = None
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        elif line.startswith('--index-url'):
            source = line
        else:
            requirements.add_package(line.strip(), source)
    required_list.close()
