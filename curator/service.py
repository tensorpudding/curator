import os
import random

import dbus
import dbus.service
import gobject
import pynotify
import gconf

from . import db

DBUS_OBJECT = 'org.curator'
DBUS_PATH = '/org/curator'
DBUS_INTERFACE = 'org.curator'

class RandomQueue(list):

    def __init__(self, list):
        random.shuffle(list)
        super(RandomQueue, self).__init__(list)
        
class DBusService(dbus.service.Object):

    def __init__(self, database, notify = True, interval = 30, listen = True):

        self.database = database
        self.notify = notify
        self.interval = interval
        self.gconf = gconf.client_get_default()
        self.current = None
        self.loop = gobject.MainLoop()
        self.listening = False

        # Update database, populate queue

        self.database.update()
        self.queue = RandomQueue(self.database.get_all_wallpapers(visible =
                                                                  True))

        self.interval_updated = False
        self.wallpaper_loop = gobject.timeout_add(self.interval*60, 
                                               self.__run_wallpaper_loop)
        self.update_db_loop = gobject.timeout_add(20, self.__run_update_db_loop)

        if listen:
            self.listen()

    def listen(self):
        # D-Bus startup magic
        bus_name = dbus.service.BusName(DBUS_OBJECT, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        name = dbus.service.BusName(DBUS_OBJECT, dbus.SessionBus())

        self.listening = True
        self.loop.run()

    def __run_wallpaper_loop(self):
        self.next_wallpaper()
        if self.interval_updated:
            self.wallpaper_loop = gobject.timeout_add(self.interval*60, 
                                                      self.__run_wallpaper_loop)
            self.interval_update = False
            return True
        else:
            return False

    def __run_update_db_loop(self):
        self.database.update()
        return False

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = '', out_signature = '')
    def next_wallpaper(self):
        """
        Choose the next wallpaper in the queue and sets it to be the background.
        """
        if self.queue == RandomQueue([]):
            # Queue is empty, let's refresh it
            visibles = self.database.get_all_wallpapers(visible = True)
            if visibles != []:
                self.queue = visibles
            else:     # no suitable wallpapers to show, do nothing
                return
        next = self.queue.pop()
        if self.database.is_hidden(next):
            self.next_wallpaper()   # try again
        else:
            self.current = next
            self.gconf.set_string("/desktop/gnome/background/" +
                                  "picture_filename", next)
            if self.listening:
                self.changed_wallpaper(next)
            if self.notify:
                pynotify.init("curator")
                self.n = pynotify.Notification("Now viewing:",
                                               os.path.basename(self.current))
                self.n.set_timeout(pynotify.EXPIRES_DEFAULT)
                self.n.show()

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = '', out_signature = '')
    def hide_current(self):
        """
        Hides the current wallpaper.
        """
        if self.current:  # make sure that we actually set a wallpaper first
            self.database.hide_wallpaper(self.current)
            if self.listening:
                self.was_hidden(self.current)
            if self.notify:
                pynotify.init("curator")
                self.n = pynotify.Notification(os.path.basename(self.current) +
                                               " has been hidden")
                self.n.set_timeout(pynotify.EXPIRES_DEFAULT)
                self.n.show()
            self.next_wallpaper()

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 's', out_signature = '')
    def hide(self, path):
        """
        Hides the given wallpaper.
        """
        if self.current == path:
            self.hide_current()
        else:
            self.database.hide_wallpaper(path)
            if self.listening:
                self.was_hidden(path)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 's', out_signature = 'b')
    def is_hidden(self, path):
        """
        Checks whether a given wallpaper is hidden.
        """
        return self.database.is_hidden(path)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 'b', out_signature = '')
    def update_notifications(self, notify):
        """
        Enable/disable notifications
        """
        self.notify = notify
        if self.listening:
            self.changed_notifications(notify)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 'n', out_signature = '')
    def update_update_interval(self, interval):
        """
        Set the wallpaper update interval, in minutes
        """
        self.interval = interval
        if self.listening:
            self.changed_update_interval(interval)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 's', out_signature = '')
    def update_wallpaper_directory(self, directory):
        """
        Set the wallpaper directory. Doing this reinitializes the database.
        """
        if directory != self.database.directory:
            self.database.reinitialize(directory)
            if self.listening:
                self.changed_directory(directory)

    @dbus.service.method(DBUS_INTERFACE, 
                         in_signature = '', out_signature = '')
    def quit(self):
        """
        Quit the D-Bus service.
        """
        if self.listening:
            self.loop.quit()

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def was_hidden(self,path):
        """
        Signal emitted when a wallpaper is hidden.
        """
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def was_revealed(self, path):
        """
        Signal emitted when a wallpaper was made visible.
        """
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def changed_wallpaper(self,path):
        """
        Signal emitted when the wallpaper is changed.
        """
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 'n')
    def changed_update_interval(self,interval):
        """
        Signal emitted when the update interval is changed.
        """
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 'b')
    def changed_notifications(self,notifications):
        """
        Signal emitted when the notification setting is changed.
        """
        pass

    @dbus.service.signal(DBUS_INTERFACE, signature = 's')
    def changed_directory(self,directory):
        """
        Signal emitted when the wallpaper directory is changed.
        """
        pass
