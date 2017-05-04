#!/usr/bin/env python
import os
import sys
try:
    from urllib import unquote
except ImportError: # python3
    from urllib.parse import unquote

import random
import shutil
import difflib
import doctest
import tempfile
import unittest
import threading
import posixpath
import subprocess as sp

try:
    from SocketServer import ThreadingMixIn
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except ImportError: # python 3
    from socketserver import ThreadingMixIn
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PKG_BASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../")
sys.path.append(PKG_BASE_PATH)

from libpip2pi import commands as pip2pi_commands

class chdir(object):
    """ A drop-in replacement for ``os.chdir`` which also acts as a context
        manager.

        >>> old_cwd = os.getcwd()
        >>> with chdir("/usr/"):
        ...     print("current dir:", os.getcwd())
        ...
        current dir: /usr
        >>> os.getcwd() == old_cwd
        True
        >>> x = chdir("/usr/")
        >>> os.getcwd()
        '/usr'
        >>> x
        chdir('/usr/', old_path='...')
        >>> x.unchdir()
        >>> os.getcwd() == old_cwd
        True
        """

    def __init__(self, new_path, old_path=None):
        self.old_path = old_path or os.getcwd()
        self.new_path = new_path
        self.chdir()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.unchdir()

    def chdir(self):
        os.chdir(self.new_path)

    def unchdir(self):
        os.chdir(self.old_path)

    def __repr__(self):
        return "%s(%r, old_path=%r)" %(
            type(self).__name__, self.new_path, self.old_path,
        )


class Pip2PiRequestHandler(SimpleHTTPRequestHandler):
    base_path = os.path.join(BASE_PATH, "assets/")

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.base_path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path


IS_CASE_INSENSITIVE = os.path.exists(__file__.upper())
OS_HAS_SYMLINK = hasattr(os, "symlink")

class Pip2PiHeavyTests(unittest.TestCase):
    SERVER_PORT = random.randint(10000, 40000)

    class BackgroundIt(threading.Thread):
        server = None
        def run(self):
            self.server.serve_forever()

    class ThreadingServer(ThreadingMixIn, HTTPServer):
        pass

    @classmethod
    def setUpClass(cls):
        cls._server_thread = cls.BackgroundIt()
        cls.server = cls.ThreadingServer(("127.0.0.1", cls.SERVER_PORT),
                                         Pip2PiRequestHandler)
        cls._server_thread.server = cls.server
        cls._server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        os.chdir(BASE_PATH)
        self._temp_dir = None
        print("\n" + "-" * 70)

    def tearDown(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir)

    def assertDirContents(self, expected_contents, dir):
        with open(expected_contents) as f:
            expected = []
            for line in f.read().splitlines():
                if line.startswith("!"):
                    prefix, _, line = line.partition(": ")
                    if prefix == "!case-sensitive":
                        if IS_CASE_INSENSITIVE:
                            continue
                    else:
                        raise AssertionError("Unexpected prefix: %s" %(prefix, ))
                if not OS_HAS_SYMLINK:
                    line, _, _ = line.partition(" -> ")
                expected.append(line)

        def describe(f):
            if not OS_HAS_SYMLINK:
                return f
            try:
                link = os.readlink(f)
            except OSError as e:
                if e.errno != 22:
                    raise
            else:
                f += " -> " + link
            return f

        with chdir(dir):
            actual = [
                describe(x[2:].decode("utf-8")) for x in
                sp.check_output(["find", "."]).splitlines()
                if x[2:]
            ]

        expected.sort()
        actual.sort()

        if actual != expected:
            print("\n" + "=" * 80 + "\n")
            for line in difflib.unified_diff(expected, actual,
                                             fromfile=expected_contents,
                                             tofile="actual"):
                print(line.rstrip())
            print("\n" + "=" * 80 + "\n")
            raise AssertionError(
                "Output dir does not contain the files listed in %s (see errors on stdout)"
                %(expected_contents, )
            )

    @property
    def temp_dir(self):
        if self._temp_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix="pip2pi-tests")
        return self._temp_dir

    @property
    def index_url(self):
        return "--index-url=http://127.0.0.1:%s/simple/" %(self.SERVER_PORT, )

    def exc(self, cmd, args):
        print("Running %s with: %s" %(cmd, args))
        return getattr(pip2pi_commands, cmd)([cmd] + args)

    def test_requirements_txt(self):
        res = self.exc("pip2pi", [
            self.temp_dir,
            self.index_url,
            "-r", "test_requirements_txt/requirements.txt",
        ])
        self.assertEqual(res, 0)
        self.assertDirContents("test_requirements_txt/expected-normal.txt", self.temp_dir)

    def test_requirements_txt_with_aggressive_normalization(self):
        res = self.exc("pip2pi", [
            self.temp_dir,
            self.index_url,
            "--aggressive-normalization",
            "-r", "test_requirements_txt/requirements.txt",
        ])
        self.assertEqual(res, 0)
        self.assertDirContents("test_requirements_txt/expected-aggressively-normalized.txt",
                               self.temp_dir)

    def test_eggs_in_packages(self):
        shutil.copy("test_eggs_in_packages/fish-1.1-py2.7.egg", self.temp_dir)
        self.exc("dir2pi", [self.temp_dir])
        self.assertDirContents("expected-eggs-in-packages.txt", self.temp_dir)

    def test_wheels(self):
        res = self.exc("pip2tgz", [
            self.temp_dir,
            self.index_url,
            "wheel",
        ])
        self.assertEqual(res, 0)
        self.assertDirContents('expected-test_wheels.txt', self.temp_dir)

    def test_get_source_with_wheels(self):
        res = self.exc("pip2pi", [
            self.temp_dir,
            self.index_url,
            "-z", "six",
        ])
        self.assertEqual(res, 0)
        self.assertDirContents('expected-test_get_source_with_wheels.txt', self.temp_dir)

    def test_building_wheels_only(self):
        res = self.exc('pip2tgz', [self.temp_dir, self.index_url, '--wheel', 'fish'])
        self.assertEqual(res, 0)
        self.assertIn('fish-1.1-py2-none-any.whl', os.listdir(self.temp_dir))


class TestIsRemoteTarget(unittest.TestCase):
    remote_targets = [
        "a:b",
        "a:/bar",
        "foo:bar",
    ]

    local_targets = [
        "foo",
        "c:\\foo\\bar",
        "z:\\things",
    ]

    def test_remote_target(self):
        for target in self.remote_targets:
            assert pip2pi_commands.is_remote_target(target), \
                    "%r is remote" %(target, )

    def test_local_target(self):
        for target in self.local_targets:
            assert not pip2pi_commands.is_remote_target(target), \
                    "%r is local" %(target, )


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(
        pip2pi_commands,
        optionflags=doctest.ELLIPSIS|doctest.IGNORE_EXCEPTION_DETAIL
    ))
    return tests


if __name__ == "__main__":
    unittest.main()
