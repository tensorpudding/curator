import unittest
import random
import sys
sys.path.append("..")
from curator import db

class CuratorDbTests(unittest.TestCase):

    def setUp(self):
        self.db = db.CurateDatabase('test.db')

    def test_add_files(self):
        pass

    def test_reject_file(self):
        pass

    def test_set_directory(self):
        pass

