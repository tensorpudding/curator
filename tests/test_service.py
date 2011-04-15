import os
import sys
import random
import time

import unittest
from mock import Mock
import dbus
import gconf

from curator import service
from curator import db

class RandomQueueTest(unittest.TestCase):

    def test_derangement(self):
        self.queue = service.RandomQueue(range(1,200))
        self.assertNotEqual(self.queue.sort(), self.queue)
        self.assertEqual(set(range(1,200)), set(self.queue))

class DBusServerTest(unittest.TestCase):

    def setUp(self):
        self.database = Mock(db.Database)
        list = [str(x) + u".png" for x in range(1,250)]
        self.database.get_all_wallpapers = Mock(return_value = list)
        self.database.is_hidden = Mock(return_value = False)       
        self.gconf = Mock(gconf.Client)
        self.dbus = service.DBusService(database = self.database,
                                        notify = False, listen = False)

    def tearDown(self):
        del(self.database)
        del(self.dbus)
        del(self.gconf)

    def test_nothing(self):
        """
        Sanity check.
        """
        pass

    def test_update(self):
        """
        Test that the database is updated on initialization.
        """
        self.assertEqual(self.database.update.call_count, 1)
        pass

    def test_next_wallpaper(self):
        """
        Test that the wallpaper actually gets set properly.
        """
        self.dbus.next_wallpaper()
        self.assertTrue(self.gconf.set_string.called)
        pass

    def test_hide_current_wallpaper(self):
        """
        Test that hiding the current wallpaper works.
        """
        self.dbus.next_wallpaper()
        current = self.dbus.current
        self.dbus.hide_current()
        self.assertEqual(self.database.hide_wallpaper.call_args,
                         ((current,),{}))

    def test_hide(self):
        """
        Test that hiding a wallpaper by name works.
        """
        self.dbus.hide(u'one.png')
        self.assertEqual(self.database.hide_wallpaper.call_args,
                         ((u'one.png',), {}))

    def test_is_hidden(self):
        self.dbus.is_hidden(u'one.png')
        self.assertEqual(self.database.is_hidden.call_args,
                         ((u'one.png',), {}))

    def test_hiding(self):
        """
        Test that it properly skips a random number of enqueued wallpapers
        which have been marked as hidden.
        """
        n = random.randint(1,12)
        side_effect = [False] + [True]*n
        def side_effects(*args, **kwargs):
            return side_effect.pop()
        self.database.is_hidden.side_effect = side_effects
        next_good = self.dbus.queue[-(n+1)]
        self.dbus.next_wallpaper()
        self.assertEqual(next_good, self.dbus.current)

if __name__=='__main__':
    unittest.main()
