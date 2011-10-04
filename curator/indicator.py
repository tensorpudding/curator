import os
import os.path
import sys

from gi.repository import Gtk
import dbus
import appindicator
import gconf

from . import service
from . import config

class CuratorIndicator():

    def __init__(self, dbus_client):

        self.ind = appindicator.Indicator("curator", "curator-tray",
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        self.dbus_client = dbus_client

        self.menu = Gtk.Menu()
        
        next = Gtk.MenuItem("Next wallpaper")
        self.menu.append(next)
        next.connect_object("activate",
                            lambda w: self.dbus_client.next_wallpaper(),
                            "Next Wallpaper")
        next.show()
        
        hide = Gtk.MenuItem("Hide wallpaper")
        self.menu.append(hide)
        hide.connect_object("activate",
                            lambda w: self.dbus_client.hide_current(),
                            "Hide wallpaper")
        hide.show()

        pref = Gtk.MenuItem("Preferences")
        self.menu.append(pref)
        pref.connect_object("activate",
                           lambda w: self.preferences(),
                           "Preferences")
        pref.show()

        about = Gtk.MenuItem("About")
        self.menu.append(about)
        about.connect_object("activate",
                             lambda w: self.about(),
                             "About")
        about.show()

        quit = Gtk.MenuItem("Quit")
        self.menu.append(quit)
        quit.connect_object("activate",
                            lambda w: self.quit(),
                            "Quit")

        quit.show()
        self.ind.set_menu(self.menu)

    def about(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__),
                                                "about.ui"))
        signals = {'on_about_close':
                       self.on_about_response,
                   'on_about_response':
                       self.on_about_response,
                   }
        builder.connect_signals(signals)
        self.about_dialog = builder.get_object("about")
        self.about_dialog.show()

    def on_about_response(self, widget, respid):
        self.about_dialog.destroy()

    def preferences(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__),
                                                "preferences.ui"))
        signals = {'on_wallpaper_directory_file_set':
                       self.on_set_directory,
                   'on_notifications_toggled':
                       self.on_toggle_notify,
                   'on_preferences_close':
                       lambda w: w.destroy(),
                   'on_okay_clicked':
                       self.on_okay_clicked,
                   'on_cancel_clicked':
                       self.on_cancel_clicked,
                   'on_update_interval_value_changed':
                       self.on_changed_interval,
                   }
        builder.connect_signals(signals)
        self.prefs_dialog = builder.get_object("preferences")
        conf = config.get()
        wallpaper_directory = builder.get_object("wallpaper_directory")
        self.directory = conf['wallpaper_directory']
        wallpaper_directory.set_current_folder(self.directory)
        notifications = builder.get_object("notifications")
        self.notifications = conf['notify']
        notifications.set_active(self.notifications)
        update_interval = builder.get_object("update_interval")
        self.update_interval = conf['interval']
        update_interval.set_value(self.update_interval)
        self.prefs_dialog.show()

    def on_changed_interval(self, adjustment):
        self.update_interval = int(adjustment.get_value())

    def on_set_directory(self, filechooser):
        self.directory = filechooser.get_current_folder()

    def on_toggle_notify(self, toggle):
        self.notifications = toggle.get_property("active")

    def on_okay_clicked(self, button):
        client = gconf.client_get_default()
        client.set_string(config.GCONF_WALLPAPER_KEY, self.directory)
        client.set_bool(config.GCONF_NOTIFY_KEY, self.notifications)
        client.set_int(config.GCONF_INTERVAL_KEY, self.update_interval)
        self.prefs_dialog.destroy()

    def on_cancel_clicked(self, button):
        self.prefs_dialog.destroy()

    def quit(self):
        self.dbus_client.quit()
        Gtk.main_quit()
                                       

def main():
    """
    Main entry point of the indicator
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
    CuratorIndicator(dbus_client)
    Gtk.main()
