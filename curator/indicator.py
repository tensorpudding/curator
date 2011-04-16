import os
import os.path
import sys
import time

import dbus
import dbus.service
import gtk
import gobject
import appindicator

from . import service
from . import watchdog

GLADE_FILE = 'curator.ui'
INDICATOR_ICON = 'curator'

GCONF_NOTIFY_KEY = '/apps/curator/notifications'
GCONF_INTERVAL_KEY = '/apps/curator/update_interval'
GCONF_WALLPAPER_KEY = '/apps/curator/wallpaper_directory'
GCONF_INDICATOR_KEY = '/apps/curator/use_indicator'

class CuratorIndicator():

    def __init__(self, dbus_client):
#         builder = gtk.Builder()
#         builder.add_from_file(os.path.join(
#                 os.path.dirname(__file__), GLADE_FILE))
#         self.preference_window = builder.get_object("preferences")
#         self.about_window = builder.get_object("about")
#         builder.connect_signals({ "on_wallpaper_directory_file_set":
#                                       self.wallpaper_callback,
#                                   })
                                       
#         self.update_adjustment = builder.get_object("interval_adjustment")

        self.ind = appindicator.Indicator("curator", INDICATOR_ICON,
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.dbus_client = dbus_client

        self.menu = gtk.Menu()
        
        next = gtk.MenuItem("Next wallpaper")
        self.menu.append(next)
        next.connect_object("activate",
                            lambda w: self.dbus_client.next_wallpaper(),
                            "Next Wallpaper")
        next.show()
        
        hide = gtk.MenuItem("Hide wallpaper")
        self.menu.append(hide)
        hide.connect_object("activate",
                            lambda w: self.dbus_client.hide_current(),
                            "Hide wallpaper")
        hide.show()

        pref = gtk.MenuItem("Preferences")
        self.menu.append(pref)
#        pref.connect_object("activate",
#                            lambda w: self.preference_window.show(),
#                            "Preferences")
        pref.show()

        about = gtk.MenuItem("About")
        self.menu.append(about)
#         about.connect_object("activate",
#                              lambda w: self.about_window.show(),
#                              "About")

        quit = gtk.MenuItem("Quit")
        self.menu.append(quit)
        quit.connect_object("activate",
                            lambda w: self.quit(),
                            "Quit")

        quit.show()
        self.ind.set_menu(self.menu)
                                    
    def wallpaper_callback(self, filechooser):
        client = gconf.client_get_default()
        client.set_string(GCONF_WALLPAPER_KEY, filechooser.get_current_folder())

    def quit(self):
        self.dbus_client.quit()
        gtk.main_quit()
                                       

def main():
    """
    Main entry point of the indicator
    """
    bus = dbus.SessionBus()
    dbus_object = bus.get_object(service.DBUS_OBJECT, service.DBUS_PATH)
    dbus_client = dbus.Interface(dbus_object, service.DBUS_INTERFACE)
    config = watchdog.GConfWatchdog()
    config.listen(dbus_client)
    CuratorIndicator(dbus_client)
    gtk.main()
