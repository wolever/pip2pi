``pip2pi`` builds a PyPI-compatible package repository from ``pip`` requirements
================================================================================

PyPI can go down, package maintainers can remove old tarballs, and downloading
tarballs can take a long time. ``pip2pi`` helps to alleviate these problems by
making it blindingly simple to maintain a PyPI-compatible repository of packages
your software depends on.

Status
------

These tools were developed to be used internally, and they appear to work for
me. I'm going to be polishing them up a bit, turning them into a proper Python
package, etc... But they should be functional for now.

Requirements
------------

0. ``pip``
1. A ``requirements.txt`` file for your project (optional, but useful)
2. An HTTP server (optional, but useful)


Setup
-----

Create the directory which will contain the tarballs of required packages,
preferably somewhere under your web server's document root::

    $ mkdir /var/www/packages/


Mirroring Packages
------------------

To mirror a package and all of its requirements, use ``pip2tgz``::

    $ pip2tgz packages/ foo==1.2
    ...
    $ ls packages/
    foo-1.2.tar.gz
    bar-0.8.tar.gz

Note that ``pip2tgz`` passes package arguments directly to ``pip``, so packages
can be specified in any format that ``pip`` recognizes::

    $ cat requirements.txt
    foo==1.2
    http://example.com/baz-0.3.tar.gz
    $ pip2tgz packages/ -r requirements.txt
    ...
    $ ls packages/
    foo-1.2.tar.gz
    bar-0.8.tar.gz
    baz-0.3.tar.gz


Building a Package Index
------------------------

A directory full of ``.tar.gz`` files can be turned into PyPI-compatible
"simple" package index using the ``dir2pi`` command::

    $ ls packages/
    bar-0.8.tar.gz
    baz-0.3.tar.gz
    foo-1.2.tar.gz
    $ dir2pi packages/
    $ find packages/
    packages/
    packages/bar-0.8.tar.gz
    packages/baz-0.3.tar.gz
    packages/foo-1.2.tar.gz
    packages/simple
    packages/simple/bar
    packages/simple/bar/bar-0.8.tar.gz
    packages/simple/baz
    packages/simple/baz/baz-0.3.tar.gz
    packages/simple/foo
    packages/simple/foo/foo-1.2.tar.gz


Using Your New Package Index
----------------------------

To use the new package index, pass the ``--use-index=`` argument to ``pip``::

    $ pip install --use-index=http://example.com/packages/simple/ foo

Or, once it has been mirrored, prefix you ``requirements.txt`` with
``--use-index=...``::

    $ cat requirements.txt
    --use-index=http://example.com/packages/simple/
    foo==1.2

Keywords
========

* Mirror PyPI
* Offline PyPI
* Create offline PyPI mirror
