# -*- encoding: utf-8 -*-
'''
    libpip2pi.actions
    ~~~~~~~~~~~~~~~~~

    execute all operations

    :copyright: (c) 2012 by David Wolever and contributors.
    :license: BSD, see LICENSE for more details.
'''


from libpip2pi.helpers import file_to_package
from subprocess import Popen
import zipfile
import tarfile
import shutil
import os

from uuid import uuid4


def get_bundle(package, outdir='/tmp', tempdir='/tmp', bundle='bundle.zip',
               get_dependencies=False):
    '''
    downloads and creates a bundle for a given package.

    :param package: the package name (in pip format)
    :param outdir: where to store the resulting bundle
    :param tempdir: the directory used to build the bundle. If this directory
    does not exist, it will be created before creating the bundle and, if the
    outdir is different from the tempdir, discarded at the end.
    :param bundle: the bundle name.
    :param ignore_dependencies: do not download dependencies of a package.
    '''

    tempdir = os.path.join(tempdir, str(uuid4()))
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)

    build_dir = os.path.join(tempdir, 'build')
    bundle_zip = os.path.join(outdir, bundle)

    command = ['pip', 'bundle', '-q', '-b', build_dir]
    if not get_dependencies:
        command += ['--no-deps']
    command += [bundle_zip, package]

    pip = Popen(command)
    pip.wait()
    if pip.returncode:
        shutil.rmtree(tempdir)
        print '%s : not found' % package
        raise ValueError('%s package : not found' % package)

    #TODO: use a real logger
    print '%s has been sucessfully bundled' % package

    shutil.rmtree(tempdir)

    return bundle_zip


def bundle_to_tgz(bundle, tempdir='/tmp', outdir='/tmp'):
    '''
    convert packages contained in a bundle to their respective tgz archives.

    :param bundle: bundle file path.

    '''

    tempdir = os.path.join(tempdir, str(uuid4()))
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)

    zipfile.ZipFile(bundle).extractall(tempdir)

    bundle_file = os.path.join(tempdir, 'pip-manifest.txt')

    for line in open(bundle_file, 'r'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        pkg_version = line.split('==')
        if len(pkg_version) != 2:
            print ('surprising line in %r: %r' % (bundle_file, line))
            raise ValueError('surprising line in %r: %r'
                             % (bundle_file, line))
        pkg, version = pkg_version
        version = version.replace('-', '_')

        old_input_dir = os.path.join(tempdir, 'build', pkg)
        new_input_dir = os.path.join(tempdir, '%s-%s' % (pkg, version))
        if os.path.exists(new_input_dir):
            shutil.rmtree(new_input_dir)
        os.rename(old_input_dir, new_input_dir)

        output_name = os.path.join(outdir,
                                   os.path.relpath(new_input_dir,
                                                   tempdir) + '.tar.gz')
        package = tarfile.open(output_name, 'w:gz')
        package.add(new_input_dir, recursive=True,
                    arcname=os.path.relpath(new_input_dir, tempdir))
        package.close()
        print ('%s : sucessfully added to your repository.' %
            (os.path.relpath(new_input_dir, tempdir) + '.tar.gz'))


    shutil.rmtree(tempdir)

def dir_to_pi(pkgdir):
    '''
    converts a directory containing tar.gz packages to a PyPI compatible
    directory tree.

    :param pkgdir: the directory to convert.
    '''

    pkgdirpath = lambda *x: os.path.join(pkgdir, *x)
    if not os.path.isdir(pkgdir):
        raise ValueError('no such directory: %r' % (pkgdir, ))
    shutil.rmtree(pkgdirpath('simple'), ignore_errors=True)
    os.mkdir(pkgdirpath('simple'))

    for file in os.listdir(pkgdir):
        pkg_filepath = os.path.join(pkgdir, file)
        if not os.path.isfile(pkg_filepath):
            continue
        pkg_basename = os.path.basename(file)
        if pkg_basename.startswith('.'):
            continue
        pkg_name, pkg_rest = file_to_package(pkg_basename, pkgdir)
        pkg_dir = pkgdirpath('simple', pkg_name)
        if not os.path.exists(pkg_dir):
            os.mkdir(pkg_dir)
        pkg_new_basename = '-'.join([pkg_name, pkg_rest])
        symlink_target = os.path.join(pkg_dir, pkg_new_basename)
        symlink_source = os.path.join('../../', pkg_basename)
        os.symlink(symlink_source, symlink_target)
