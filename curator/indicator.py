import os
import os.path
import sys

from gi.repository import Gtk
import dbus
import gconf

from . import service
from . import config

class Curator(object):
    """
    Main class for Curator program.
    """
    def __init__(self, dbus_client):
        """
        Initialize the tray icon, hook up signals, etc.
        """
        self.dbus_client = dbus_client

        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__),
                                           "curator.ui"))
        # Get objects
        self.curator = builder.get_object("curator")
        self.curator.set_from_icon_name("curator")
        self.curator_menu = builder.get_object("curator_menu")
        self.next_item = builder.get_object("next_item")
        self.hide_item = builder.get_object("hide_item")
        self.about_item = builder.get_object("about_item")
        self.quit_item = builder.get_object("quit_item")
        self.curator_menu.show_all()

        # Set signals
        self.curator.connect("popup-menu", self.popup_menu)
        self.next_item.connect("activate", self.next_wallpaper)
        self.hide_item.connect("activate", self.hide_wallpaper)
        self.quit_item.connect("activate", self.quit)

    def popup_menu(self, status, button, activate_time):
        """
        Pop up the Curator menu.
        """
        self.curator_menu.popup(None, None, None, None, button, activate_time)

    def next_wallpaper(self, menu_item):
        """
        GTK callback sends D-Bus signal to switch to next wallpaper.
        """
        self.dbus_client.next_wallpaper()

    def hide_wallpaper(self, menu_item):
        """
        GTK callback sends D-Bus signal to hide current wallpaper, then
        switches to the next.
        """
        self.dbus_client.hide_current()

    def quit(self, menu_item):
        """
        Quits Curator
        """
        self.dbus_client.quit()
        Gtk.main_quit()
                                       
def main():
    """
    Main entry point.
    """
    # First, attempt to connect to DBus service
    # If you can't, then give up.
    try:
        bus = dbus.SessionBus()
        dbus_object = bus.get_object(service.DBUS_OBJECT, service.DBUS_PATH)
        dbus_client = dbus.Interface(dbus_object, service.DBUS_INTERFACE)
    except:
        print 'Could not connect to D-Bus backend!'
        sys.exit(1)

    watchdog = config.GConfWatchdog(dbus_client)
    Curator(dbus_client)
    Gtk.main()
