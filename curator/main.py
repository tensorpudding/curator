import os
import os.path
import sys
import time

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gtk
import gobject
import appindicator

from . import service
from . import watchdog
from . import db

GLADE_FILE = 'curator.ui'
#INDICATOR_ICON = 'curator48x48.png'
#ATTENTION_ICON = 'curator48x48.png'
INDICATOR_ICON = 'indicator-messages'
ATTENTION_ICON = 'indicator-messages'

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
        self.ind.set_attention_icon(ATTENTION_ICON)
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
                                       

def get_db_path():
    db_path = os.path.join(os.getenv('HOME'),
                           '.local/share/curator/wallpapers.db')
    if not os.path.isdir(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    return db_path

def main():
    """
    Main entry point of the program
    """
    config = watchdog.GConfWatchdog()
    notify = config.get()['notify']
    interval = config.get()['interval']
    wallpaper_directory = config.get()['wallpaper_directory']
    db_path = get_db_path()
    try:
        pid = os.fork()
        if pid == 0:
            database = db.Database(wallpaper_directory, path = db_path)
            DBusGMainLoop(set_as_default=True)
            service.DBusService(database = database,
                                notify = notify,
                                interval = interval,
                                listen = True)
        else:
            time.sleep(2)
            bus = dbus.SessionBus()
            dbus_object = bus.get_object(service.DBUS_OBJECT, service.DBUS_PATH)
            dbus_client = dbus.Interface(dbus_object, service.DBUS_INTERFACE)
            config.listen(dbus_client)
            CuratorIndicator(dbus_client)
            gtk.main()

    except IOError:
        print "Couldn't fork!"
