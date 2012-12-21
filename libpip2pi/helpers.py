# -*- encoding: utf-8 -*-
'''
    libpip2pi.helpers
    ~~~~~~~~~~~~~~~~~

    provides some helper functions

    :copyright: (c) 2012 by David Wolever and contributors.
    :license: BSD, see LICENSE for more details.
'''


def file_to_package(file, basedir=None):
    ''' Returns the package name for a given file.

        >>> file_to_package('foo-1.2.3_rc1.tar.gz')
        ('foo', '1.2.3-rc1.tar.gz')
        >>> file_to_package('foo-bar-1.2.tgz')
        ('foo-bar', '1.2.tgz')
        >>>
    '''
    split = file.rsplit('-', 1)
    if len(split) != 2:
        msg = 'unexpected file name: %r ' % (file, )
        msg += '(not in "pkg-name-version.xxx" format'
        if basedir:
            msg += '; found in directory: %r' % (basedir)
        msg += ')'
        raise ValueError(msg)
    # Note: for various reasions (which I don't 100% remember right now) we
    # need to replace '-' in the version string with '_'. I think this has to
    # do with the way we export the list of files from the PIP manifest, then
    # read them back in somewhere else. It would be cool to fix this at some
    # point.
    return (split[0], split[1].replace('_', '-'))
