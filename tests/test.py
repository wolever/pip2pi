#!/usr/bin/env python
import os
import urllib
import random
import shutil
import thread
import tempfile
import posixpath
import unittest2
import subprocess
import SocketServer
import SimpleHTTPServer

from libpip2pi import commands as pip2pi_commands

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

class chdir(object):
    """ A drop-in replacement for ``os.chdir`` which also acts as a context
        manager.

        >>> old_cwd = os.getcwd()
        >>> with chdir("/usr/"):
        ...     print "current dir:", os.getcwd()
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


class Pip2PiRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    base_path = os.path.join(BASE_PATH, "assets/")

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.base_path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path


class Pip2PiTests(unittest2.TestCase):
    SERVER_PORT = random.randint(10000, 40000)

    @classmethod
    def setUpClass(cls):
        server_ready = thread.allocate_lock()
        server_ready.acquire()
        cls._server_thread = thread.start_new_thread(cls.spawn_http_server,
                                                     (server_ready, ))
        server_ready.acquire()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    @classmethod
    def spawn_http_server(cls, ready_lock):
        cls.server = SocketServer.TCPServer(("127.0.0.1", cls.SERVER_PORT),
                                            Pip2PiRequestHandler)
        ready_lock.release()
        cls.server.serve_forever()

    def setUp(self):
        os.chdir(BASE_PATH)
        self._temp_dir = None
        print "\n" + "-" * 70

    def tearDown(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir)

    def assertDirsEqual(self, a, b):
        res = subprocess.call(["diff", "-x", "*.tar.gz", "-r", a, b])
        if res:
            with chdir(a):
                print "1st directory:", a
                subprocess.call(["find", "."])
            with chdir(b):
                print "2nd directory:", b
                subprocess.call(["find", "."])
            raise AssertionError("Directories %r and %r differ! (see errors "
                                 "printed to stdout)" %(a, b))

    @property
    def temp_dir(self):
        if self._temp_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix="pip2pi-tests")
        return self._temp_dir

    @property
    def index_url(self):
        return "--index-url=http://127.0.0.1:%s/simple/" %(self.SERVER_PORT, )

    def exc(self, cmd, args):
        print "Running %s with: %s" %(cmd, args)
        return getattr(pip2pi_commands, cmd)([cmd] + args)

    def test_requirements_txt(self):
        res = self.exc("pip2pi", [
            self.temp_dir,
            self.index_url,
            "-r", "test_requirements_txt/requirements.txt",
        ])
        self.assertEqual(res, 0)
        self.assertDirsEqual("test_requirements_txt/expected/", self.temp_dir)

    def test_eggs_in_packages(self):
        shutil.copy("test_eggs_in_packages/fish-1.1-py2.7.egg", self.temp_dir)
        self.exc("dir2pi", [self.temp_dir])
        self.assertDirsEqual("test_eggs_in_packages/", self.temp_dir)

if __name__ == "__main__":
    unittest2.main()
