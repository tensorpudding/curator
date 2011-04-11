import threading
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import random
import gconf

import db

DBUS_OBJECT = 'org.curator'
DBUS_PATH = '/org/curator'
DBUS_INTERFACE = 'org.curator'

class GConf():
    def __init__(self):
        self.gclient = gconf.client_get_default()

class DBusService(dbus.service.Object):

    class Queue(list):

        def __init__(self, list):
            random.shuffle(list)
            list.__init__(self, list)

        def next(self):
            return self.pop()

        def append(self, item):
            list.append(self, item)
            random.shuffle(self)

    def __init__(self):
        # Start up object service
        bus_name = dbus.service.BusName(DBUS_OBJECT, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        # Initialize database connection
        self.db = db.Database('/home/michael/.local/share/curator/curator.db')
        # Initialize queue
        self.queue = Queue(self.db.select_all_nonrejects())
        # Get config from GConf
        pass

    def __del__(self):
        pass

    def __set_wallpaper(self,key):
        name, path, rej = self.db.get_entry_by_key(key)
        # set wallpaper here...
        if rej > 0:
            self.__set_wallpaper(self.queue.next)
        else:
            self.current = key
            self.changed_wallpaper(path)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = '', out_signature='')
    def next_wallpaper(self):
        self.__set_wallpaper(self.queue.next)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = '', out_signature='')
    def reject_current_wallpaper(self):
        self.db.reject_by_key(self.current)
        self.next_wallpaper()

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 's', out_signature='')
    def reject_wallpaper_by_path(self, path):
        self.db.reject_by_path(path)

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def rejected_wallpaper(self,path):
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def unrejected_wallpaper(self,path):
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def changed_wallpaper(self,path):
        pass

    def update_wallpapers(self):
        pass

class DBusThread(threading.Thread):
    def run(self):
        DBusGMainLoop(set_as_default=True)
        object = DBusService()
        gtk.main()
