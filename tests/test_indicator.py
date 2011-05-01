import unittest
import time

import gtk
from mock import Mock, patch

from curator import indicator
from curator import service

# Stolen from http://unpythonic.blogspot.com/2007/03/unit-testing-pygtk.html
def refresh_gui(delay = 0):
    while gtk.events_pending():
        gtk.main_iteration_do(block=False)
    time.sleep(delay)

class IndicatorTests(unittest.TestCase):
    @patch('gconf.client_get_default')
    @patch('gtk.Menu')
    @patch('gtk.MenuItem')
    @patch('gtk.Builder')
    @patch('appindicator.Indicator')
    def setUp(self, *args):
        dbus_client = Mock(service.DBusService)
        self.indicator = indicator.CuratorIndicator(dbus_client)

    def test_pass(self, *args):
        pass
