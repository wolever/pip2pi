#!/usr/bin/env python
import os
import urllib
import random
import shutil
import thread
import tempfile
import posixpath
import unittest2
import SocketServer
import SimpleHTTPServer
from subprocess import check_call

from libpip2pi.commands import pip2pi

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

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

    def tearDown(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir)

    def assertDirsEqual(self, a, b):
        check_call(["diff", "-x", "*.tar.gz", "-r", a, b])

    @property
    def temp_dir(self):
        if self._temp_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix="pip2pi-tests")
        return self._temp_dir

    @property
    def index_url(self):
        return "--index-url=http://127.0.0.1:%s/simple/" %(self.SERVER_PORT, )

    def pip2pi(self, args):
        print "Running pip2pi with:", args
        return pip2pi(["pip2pi"] + args)

    def test_requirements_txt(self):
        res = self.pip2pi([
            self.temp_dir,
            self.index_url,
            "-r", "test_requirements_txt/requirements.txt",
        ])
        self.assertEqual(res, 0)
        self.assertDirsEqual("test_requirements_txt/expected/", self.temp_dir)

if __name__ == "__main__":
    unittest2.main()
