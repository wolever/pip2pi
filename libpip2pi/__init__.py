# -*- encoding: utf-8 -*-
'''
    libpip2pi
    ~~~~~~~~~

    A library to build a PyPI-compatible package repository from pip
    requirements.

    :copyright: (c) 2012 by David Wolever.
    :license: BSD, see LICENSE for more details.
'''


from libpip2pi.parser import get_parser
from libpip2pi.actions import get_bundle, bundle_to_tgz
from libpip2pi.requirements import Requirements, parse_file
import shutil
import os

__version__ = (0, 1, 5)


def main():
    args = get_parser().parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    if not os.path.exists(args.build):
        os.mkdir(args.build)

    if args.requirements is None and args.package == []:
        get_parser().print_help()
        return 0

    requirements = Requirements()
    if args.requirements is not None:
        parse_file(requirements, args.requirements)

    for package, source in requirements:
        try:
            bundle_to_tgz(get_bundle(package, args.build, args.build,
                                     get_dependencies=args.dependencies),
                          args.build, args.output)
        except:
            if not args.ignore_missing:
                return 0
            pass
    shutil.rmtree(args.build)

