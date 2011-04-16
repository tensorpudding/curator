import os
import sys
import random
import time

import unittest
from mock import Mock, patch
import dbus
import gconf
import pynotify

from curator import service
from curator import db

class RandomQueueTest(unittest.TestCase):

    def test_derangement(self):
        self.queue = service.RandomQueue(range(1,200))
        self.assertNotEqual(self.queue.sort(), self.queue)
        self.assertEqual(set(range(1,200)), set(self.queue))

class DBusServerTest(unittest.TestCase):

    @patch('gconf.client_get_default')
    def setUp(self, mock_get):
        self.mockclient = Mock()
        mock_get.return_value = self.mockclient
        self.database = Mock(db.Database)
        list = [str(x) + u".png" for x in range(1,250)]
        self.database.get_all_wallpapers = Mock(return_value = list)
        self.database.is_hidden = Mock(return_value = False)       
        self.dbus = service.DBusService(database = self.database,
                                        notify = False, listen = False)

    def tearDown(self):
        del(self.database)
        del(self.dbus)

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
        self.dbus.next_wallpaper()
        self.assertTrue(self.mockclient.set_string.called)


#     def test_next_wallpaper(self):
#         gconf = Mock()
#         self.dbus.gconf = gconf
#         self.dbus.next_wallpaper()
#         self.assertTrue(gconf.set_string.called)


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

    @patch('pynotify.Notification')
    def test_notifications(self, MockNotification):

        self.dbus.update_notifications(True)
        self.dbus.next_wallpaper()
        self.assertTrue(MockNotification.called)
        MockNotification.called = False
        self.dbus.hide_current()
        self.assertTrue(MockNotification.called)
        MockNotification.called = False

        self.dbus.update_notifications(False)
        self.dbus.next_wallpaper()
        self.assertFalse(MockNotification.called)
        MockNotification.called = False
        self.dbus.hide_current()
        self.assertFalse(MockNotification.called)

if __name__=='__main__':
    unittest.main()
