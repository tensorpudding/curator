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

GCONF_NOTIFY_KEY = '/apps/curator/interface/notifications'
GCONF_INTERVAL_KEY = '/apps/curator/backend/update_interval'
GCONF_INDICATOR_KEY = '/apps/curator/interface/indicator'


class Queue(list):

    def __init__(self, list):
        list.__init__(self)
        random.shuffle(list)
        self.append(list)


    def next(self):
        return self.pop()

    def append(self, item):
        list.append(self, item)
        random.shuffle(self)

class DBusService(dbus.service.Object):

    def __init__(self):
        # Start up object service
        bus_name = dbus.service.BusName(DBUS_OBJECT, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        # Initialize database connection
        self.db = db.Database('/home/michael/.local/share/curator/curator.db')
        # Initialize cache
        self.cache = set(self.db.select_all_paths())
        # Start update looper
        self.update_timer = gobject.timeout_add(10000, self.update_wallpapers)
        # Initialize queue
        self.queue = Queue([])
        self.__refresh_queue()
        # Get config from GConf
        self.gclient = gconf.client_get_default()
        notify = self.gclient.get_bool(GCONF_NOTIFY_KEY)
        if notify == None:
            notify = True
            self.gclient.set_bool(GCONF_NOTIFY_KEY, notify)
        self.notify = notify
        interval = self.gclient.get_int(GCONF_INTERVAL_KEY)
        if interval == None:
            interval = 30
            self.gclient.set_int(GCONF_INTERVAL_KEY, interval)
        self.interval = interval
        # Start the wallpaper switcher
        self.wallpaper_timer = gobject.timeout_add(60000*self.interval,
                                                   self.next_wallpaper)
        # Switch wallpaper for the first time
        self.next_wallpaper()

    def __refresh_queue(self):
        self.queue.append(self.db.select_all_nonrejects())

    def __set_wallpaper(self,key):
        name, path, rej = self.db.get_entry_by_key(key)
        # If queue is empty, refresh it
        if self.queue == Queue():
            self.__refresh_queue()
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
        return True

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
        return path

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def unrejected_wallpaper(self,path):
        return path

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def changed_wallpaper(self,path):
        return path

    def update_wallpapers(self):
        self.cache = self.db.update(self.cache)
        return True

class DBusThread(threading.Thread):
    def run(self):
        DBusGMainLoop(set_as_default=True)
        object = DBusService()
        loop = gobject.MainLoop()
        loop.run()
