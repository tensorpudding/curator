"""Runs a series of tests on the database module."""
import os
import os.path
import sys
import random

import unittest
from mock import Mock, patch

from curator import db

LOCATION = os.path.join(os.getcwd(),'wallpapers')

class CuratorDbTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        os.mkdir(LOCATION)
        for n in range(1,250):
            open(os.path.join(LOCATION, "test" + str(n) + ".png"), 'w').close()
        os.mkdir(LOCATION + '2')
        for n in range(1,250):
            open(os.path.join(LOCATION + '2',
                              "test" + str(n) + ".png"), 'w').close()

    @classmethod
    def tearDownClass(self):
        for n in range(1,250):
            os.remove(os.path.join(LOCATION, "test" + str(n) + ".png"))
        os.rmdir(LOCATION)
        for n in range(1,250):
            os.remove(os.path.join(LOCATION + '2', "test" + str(n) + ".png"))
        os.rmdir(LOCATION + '2')


    def setUp(self):
        self.database = db.Database(LOCATION)
        self.database.thumbnailer = Mock()
        self.database.thumbnailer.generate = Mock(return_value=u"123456789.png")
        self.database.thumbnailer.delete = Mock()

    def test_passing(self):
        """
        Test fails if setUp/tearDown produce errors
        This is the sanity check
        """
        pass

    def test_add_remove_wallpaper(self):
        """
        Test adding, then removing, a single wallpaper by path
        """
        test = os.path.join(LOCATION, 'test0.png')
        open(test, 'w').close()
        self.database.update()
        wallpapers = self.database.get_all_wallpapers()
        self.assertTrue(test in wallpapers)
        os.remove(test)
        self.database.update()
        wallpapers = self.database.get_all_wallpapers()
        self.assertFalse(test in wallpapers)

    def test_update_idempotent(self):
        """
        Test that updating leaves database unchanged when there are no new items
        """
        self.database.reinitialize()
        before = self.database.get_all_wallpapers()
        self.database.update()
        after = self.database.get_all_wallpapers()
        self.assertEqual(before, after)

    def test_set_directory(self):
        """
        Test that setting the directory works.
        """
        self.database.reinitialize(LOCATION + '2')
        after = self.database.get_all_wallpapers()
        self.assertTrue(os.path.join(LOCATION + '2', "test1.png") in after)

    def test_get_thumbnail(self):
        """
        Test that getting a thumbnail works.
        """
        pass
        
if __name__=='__main__':
    unittest.main()
