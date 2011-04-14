"""Runs a series of tests on the thumbnailer module."""
import os
import os.path
import sys
import random

import unittest
from mock import Mock

from curator import thumbnail

class CuratorThumbnailerTests(unittest.TestCase):

    def setUp(self):
        self.thumbnailer = thumbnail.ThumbnailGenerator()

    def test_init(self):
        pass

    def test_generate(self):
        pass

if __name__=='__main__':
    unittest.main()
