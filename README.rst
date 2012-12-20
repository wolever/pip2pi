``pip2pi`` builds a PyPI-compatible package repository from ``pip`` requirements
================================================================================

PyPI can go down, package maintainers can remove old tarballs, and downloading
tarballs can take a long time. ``pip2pi`` helps to alleviate these problems by
making it blindingly simple to maintain a PyPI-compatible repository of packages
your software depends on.


Status
------

This tool was developed to create disconnected PyPI-compatible repository. It
is currently based on ``pip`` through calls to shell commands and could break
on few situations. 


Requirements
------------

``pip`` should be installed on your system.

Setup
-----

Install ``pip2pi``::

    $ pip install git+https://github.com/morgan-del/pip2pi.git


Create your repository
----------------------

    $ pip2pi -r requirements.txt -o /path/to/your/repository

This will put all the packages listed in ``requirements.txt`` under the 
specified directory. If the directory does not exist, it will be created in the
process. This directory will have the required structure to serve it as a
PyPI repository.

If a package is unavailable on PyPI, you could bypass it with the ``-i``
options, otherwise pip2pi will stop on this packet.

Using a requirements list file is not necessary, you can also manually specify
the packages you want to install::

    $ pip2pi -o /path/to/your/repository Flask werkzeug jinja2

You also can let ``pip`` handle dependencies::

    $ pip2pi -d -o /path/to/your/repository Flask

If you want a list of all available options simply do ``pip2pi -h``.


Using Your New Package Index
----------------------------

To use the new package index, serve it with a web a server and pass the 
``--use-index=`` argument to ``pip``::

    $ pip install --use-index=http://example.com/packages/simple/ foo

Or, once it has been mirrored, prefix you ``requirements.txt`` with
``--use-index=...``::

    $ cat requirements.txt
    --use-index=http://example.com/packages/simple/
    foo==1.2


Without a web server
--------------------

You can use your package index offline, too::

    $ pip install --no-download --download-cache=/var/www/packages/ foo==1.2



Keywords
========

* Mirror PyPI
* Offline PyPI
* Create offline PyPI mirror
