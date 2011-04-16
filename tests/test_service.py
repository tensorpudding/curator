import os
import sys
import random
import time

import unittest
from mock import Mock, patch

from curator import service
from curator import db

@patch('gobject.timeout_add')
@patch('gobject.source_remove')
@patch('gconf.client_get_default')
@patch('pynotify.Notification')
class DBusServerTest(unittest.TestCase):

    @patch('gobject.timeout_add')
    @patch('gobject.source_remove')
    @patch('gconf.client_get_default')
    @patch('pynotify.Notification')
    def setUp(self, MockNotification, mock_get, *args):
        self.mockclient = Mock()
        mock_get.return_value = self.mockclient
        self.database = Mock(db.Database)
        list = [str(x) + u".png" for x in range(1,250)]
        self.database.get_all_wallpapers = Mock(return_value = list)
        self.database.is_hidden = Mock(return_value = False)       
        self.database.directory = 'somewhere'
        self.dbus = service.DBusService(database = self.database,
                                        notify = False, listen = False)

    def tearDown(self, *args):
        del(self.database)
        del(self.dbus)

    def test_nothing(self, *args):
        """
        Sanity check.
        """
        pass

    def test_update(self, *args):
        """
        Test that the database is updated on initialization.
        """
        self.assertEqual(self.database.update.call_count, 1)
        pass


    def test_next_wallpaper(self, *args):
        self.dbus.next_wallpaper()
        self.assertTrue(self.mockclient.set_string.called)

    def test_hide_current_wallpaper(self, *args):
        """
        Test that hiding the current wallpaper works.
        """
        self.dbus.next_wallpaper()
        current = self.dbus.current
        self.dbus.hide_current()
        self.assertEqual(self.database.hide_wallpaper.call_args,
                         ((current,),{}))

    def test_hide(self, *args):
        """
        Test that hiding a wallpaper by name works.
        """
        self.dbus.hide(u'one.png')
        self.assertEqual(self.database.hide_wallpaper.call_args,
                         ((u'one.png',), {}))

    def test_is_hidden(self, *args):
        self.dbus.is_hidden(u'one.png')
        self.assertEqual(self.database.is_hidden.call_args,
                         ((u'one.png',), {}))

    def test_hiding(self, *args):
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

    def test_notifications(self, MockNotification, *args):

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

    def test_timeouts(self, skipone, skiptwo, mock_remove, mock_timeout):
        mock_timeout.called = False
        self.assertFalse(mock_remove.called)
        self.dbus.update_wallpaper_directory('somewhere else')
        self.assertTrue(mock_remove.called)
        self.assertTrue(mock_timeout.called)

    def test_timeout_update(self, skipone, skiptwo, mock_remove, mock_timeout):
        mock_timeout.called = False
        self.assertFalse(mock_remove.called)
        n = random.choice(range(1,300))
        self.dbus.update_update_interval(n)
        self.assertTrue(mock_remove.called)
        self.assertTrue(mock_timeout.call_args[0][0] == 60000 * n)

if __name__=='__main__':
    unittest.main()
