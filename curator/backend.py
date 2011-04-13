import os
import random

import dbus
import dbus.service
import gobject
import pynotify

import db

DBUS_OBJECT = 'org.curator'
DBUS_PATH = '/org/curator'
DBUS_INTERFACE = 'org.curator'

GCONF_NOTIFY_KEY = '/apps/curator/interface/notifications'
GCONF_INTERVAL_KEY = '/apps/curator/backend/update_interval'
GCONF_INDICATOR_KEY = '/apps/curator/interface/indicator'

class Queue(list):

    def __init__(self, list):
        random.shuffle(list)
        super(Queue, self).__init__(list)
        
class DBusService(dbus.service.Object):

    def __init__(self, database, notify = False, interval = 30,
                 start_loop = True, loop = gobject.MainLoop()):
        self.notify = notify
        self.interval = interval
        self.current = None
        self.started = False
        self.loop = loop

        self.database = database
        self.database.update()
        self.queue = Queue(self.database.get_all_wallpapers(visible = True))
        print self.queue

        self.wallpaper_loop = gobject.timeout_add(self.interval*60, 
                                               self.__run_wallpaper_loop)
        self.update_db_loop = gobject.timeout_add(20, self.__run_update_db_loop)
        if start_loop:
            self.start()

    def start(self):
        bus_name = dbus.service.BusName(DBUS_OBJECT, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        self.started = True
        self.loop.run()

    def __run_wallpaper_loop(self):
        self.next_wallpaper()
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
        if self.queue == Queue([]):
            self.queue = Queue(self.database.get_all_wallpapers(visible = True))
        if self.queue != Queue([]):
            next = self.queue.pop()
            if self.database.is_hidden(next):
                self.next_wallpaper()
            else:
                self.current = next
        ###
        # SET WALLPAPER STUFF GOES HERE
        ###
                if self.started:
                    self.changed_wallpaper(next)
                if self.notify:
                    n = pynotify.Notification("Now viewing:",
                                              os.path.basename(self.current))
                    n.show()

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = '', out_signature = '')
    def hide_current(self):
        """
        Hides the current wallpaper.
        """
        if self.current:
            self.database.hide_wallpaper(self.current)
            if self.notify:
                n = pynotify.Notification(os.path.basename(self.current) +
                                          " has been hidden")
                n.show()
            if self.started:
                self.was_hidden(self.current)
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
            if self.started:
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
        if self.started:
            self.changed_notifications(notify)

    @dbus.service.method(DBUS_INTERFACE,
                         in_signature = 'n', out_signature = '')
    def update_update_interval(self, interval):
        """
        Set the wallpaper update interval, in minutes
        """
        self.interval = interval
        if self.started:
            self.changed_interval(interval)

    @dbus.service.method(DBUS_INTERFACE, 
                         in_signature = '', out_signature = '')
    def quit(self):
        """
        Quit the D-Bus service.
        """
        if self.started:
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
