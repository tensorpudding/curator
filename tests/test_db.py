"""Runs a series of tests on the database module."""
import os
import os.path
import sys
import random

import unittest

sys.path.append("..")
from curator import db

WALLPAPERS = os.path.join(os.getcwd(),'wallpapers')

class CuratorDbTests(unittest.TestCase):

    def setUp(self):
        self.database = db.Database(WALLPAPERS)

    def tearDown(self):
        del(self.database)

    def test_passing(self):
        """
        Test fails if setUp/tearDown produce errors
        This is the sanity check
        """
        pass

    def test_add_wallpaper(self):
        """
        Test adding a single wallpaper by path
        """
        test1 = os.path.join(WALLPAPERS, "test1.png")
        self.database.add_wallpaper(test1)
        wallpapers = self.database.get_all_wallpapers()
        self.assertTrue(test1 in wallpapers)

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
        newfile = os.path.join(WALLPAPERS, "test0.png")
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

    def test_zzz_cleanup(self):
        for file in files:
            os.remove(file)
        os.rmdir(WALLPAPERS)

if __name__=='__main__':
    os.mkdir(WALLPAPERS)
    files = []
    for n in range(1,3):
        files.append(os.path.join(WALLPAPERS, "test" + str(n) + ".png"))
    for file in files:
        open(file, 'w').close()
    unittest.main()
