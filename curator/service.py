import os
import os.path

from gi.repository import Gio
from gi.repository import GObject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import pynotify

from . import db
from . import config
from .queue import RandomQueue

DBUS_OBJECT = 'org.curator'
DBUS_PATH = '/org/curator'
DBUS_INTERFACE = 'org.curator'

GSETTINGS_WALLPAPER = 'org.gnome.desktop.background'

class DBusService(dbus.service.Object):

    def __init__(self, database, notify = True, interval = 30):
        bus_name = dbus.service.BusName(DBUS_OBJECT, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        name = dbus.service.BusName(DBUS_OBJECT, dbus.SessionBus())

        self.database = database
        self.notify = notify
        self.interval = interval

        self.current = None
        self.gsettings = Gio.Settings.new(GSETTINGS_WALLPAPER)
        self.loop = GObject.MainLoop()

        # Update database, populate queue

        self.database.update()
        self.queue = RandomQueue(self.database.get_all_wallpapers(visible =
                                                                  True))
        self.wallpaper_loop = GObject.timeout_add(self.interval*60000, 
                                               self.__run_wallpaper_loop)
        self.next_wallpaper()

        self.loop.run()

    def __run_wallpaper_loop(self):
        self.next_wallpaper()
        return True

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = '', out_signature = '')
    def next_wallpaper(self):
        """
        Choose the next wallpaper in the queue and sets it to be the background.
        """
        if self.queue == RandomQueue([]):
            # Queue is empty, let's refresh it
            self.database.update()
            visibles = self.database.get_all_wallpapers(visible = True)
            if visibles != []:
                self.queue = RandomQueue(visibles)
            else:     # no suitable wallpapers to show, do nothing
                return
        next = self.queue.pop()
        if self.database.is_hidden(next):
            self.next_wallpaper()   # try again
        else:
            self.current = next
            self.gsettings.set_string("picture-uri", "file://" + next)
            GObject.source_remove(self.wallpaper_loop)
            self.wallpaper_loop = GObject.timeout_add(self.interval*60000, 
                                               self.__run_wallpaper_loop)
            self.changed_wallpaper(next)
            if self.notify:
                pynotify.init("curator")
                self.n = pynotify.Notification("Now viewing:",
                                               os.path.basename(next))
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
            self.was_hidden(path)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 's', out_signature = '')
    def reveal(self, path):
        """
        Unhides the given wallpaper.
        """
        self.database.reveal_wallpaper(path)
        self.was_revealed(path)

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

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 'n', out_signature = '')
    def update_update_interval(self, interval):
        """
        Set the wallpaper update interval, in minutes
        """
        self.interval = interval
        GObject.source_remove(self.wallpaper_loop)
        self.wallpaper_loop = GObject.timeout_add(self.interval*60000, 
                                                  self.__run_wallpaper_loop)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 's', out_signature = '')
    def update_wallpaper_directory(self, directory):
        """
        Set the wallpaper directory. Doing this reinitializes the database.
        """
        if directory != self.database.directory:
            if self.notify:
                pynotify.init("curator")
                self.n = pynotify.Notification("Reinitializing database...")
                self.n.set_timeout(pynotify.EXPIRES_DEFAULT)
                self.n.show()
            GObject.source_remove(self.wallpaper_loop)
            self.queue = RandomQueue([])
            self.database.reinitialize(directory)
            self.wallpaper_loop = GObject.timeout_add(self.interval*60000, 
                                                  self.__run_wallpaper_loop)

    @dbus.service.method(DBUS_INTERFACE, 
                         in_signature = '', out_signature = '')
    def quit(self):
        """
        Quit the D-Bus service.
        """
        GObject.source_remove(self.wallpaper_loop)
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

def main():
    """
    Main entry point for dbus service process.
    """
    db_path = os.path.join(os.getenv('HOME'),
                           '.local/share/curator/wallpapers.db')
    if not os.path.isdir(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    _config = config.get()
    notify = _config['notify']
    interval = _config['interval']
    wallpaper_directory = _config['wallpaper_directory']
    database = db.Database(wallpaper_directory, path = db_path)
    DBusGMainLoop(set_as_default=True)
    DBusService(database = database, notify = notify,
                interval = interval)
