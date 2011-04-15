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
        self.__files = []
        for n in range(1,3):
            self.__files.append(os.path.join(LOCATION,
                                             "test" + str(n) + ".png"))
        for file in self.__files:
            open(file, 'w').close()

    @classmethod
    def tearDownClass(self):
        for file in self.__files:
            os.remove(file)
        os.rmdir(LOCATION)

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
        test1 = os.path.join(LOCATION, "test1.png")
        self.database.add_wallpaper(test1)
        wallpapers = self.database.get_all_wallpapers()
        self.assertTrue(test1 in wallpapers)
        self.database.remove_wallpaper(test1)
        wallpapers = self.database.get_all_wallpapers()
        self.assertFalse(test1 in wallpapers)


    def test_update_idempotent(self):
        """
        Test that updating leaves database unchanged when there are no new items
        """
        self.database.reinitialize()
        before = self.database.get_all_wallpapers()
        self.database.update()
        after = self.database.get_all_wallpapers()
        self.assertEqual(before, after)

    def test_update_when_new(self):
        """
        Test that updating adds new files when new files exist.
        """
        self.database.reinitialize()
        before = self.database.get_all_wallpapers()
        # Let's touch a new file
        newfile = os.path.join(LOCATION, "test0.png")
        open(newfile, 'w').close()
        self.database.update()
        after = self.database.get_all_wallpapers()
        os.remove(newfile)
        self.assertNotIn(newfile, before)
        self.assertIn(newfile, after)

    def test_set_directory(self):
        """
        Test that setting the directory works.
        """
        pass

    def test_get_thumbnail(self):
        """
        Test that getting a thumbnail works.
        """
        pass
        
if __name__=='__main__':
    unittest.main()
