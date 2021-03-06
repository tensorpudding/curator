import gconf

GCONF_DIR = '/apps/curator'
GCONF_NOTIFY_KEY = '/apps/curator/notifications'
GCONF_INTERVAL_KEY = '/apps/curator/update_interval'
GCONF_WALLPAPER_KEY = '/apps/curator/wallpaper_directory'

def get():
    """
    Fetch the current state of configuration, return a dict
    """
    client = gconf.client_get_default()
    notify = client.get_bool(GCONF_NOTIFY_KEY)
    interval = client.get_int(GCONF_INTERVAL_KEY)        
    wallpaper_directory = client.get_string(GCONF_WALLPAPER_KEY)
    return { 'notify': notify, 'interval': interval,
             'wallpaper_directory': wallpaper_directory }

class GConfWatchdog(object):

    def __init__(self, dbus_client):
        """
        Begin listening on gconf, sending signals through the given D-Bus
        client.
        """
        self.client = gconf.client_get_default()
        self.client.add_dir(GCONF_DIR, gconf.CLIENT_PRELOAD_ONELEVEL)
        self.dbus_client = dbus_client
        self.client.notify_add(GCONF_NOTIFY_KEY, self.notify_callback)
        self.client.notify_add(GCONF_INTERVAL_KEY, self.interval_callback)
        self.client.notify_add(GCONF_WALLPAPER_KEY, self.wallpaper_callback)

    def notify_callback(self, client, *args, **kwargs):
        notify = self.client.get_bool(GCONF_NOTIFY_KEY)
        self.dbus_client.update_notifications(notify)

    def interval_callback(self, client, *args, **kwargs):
        interval = self.client.get_int(GCONF_INTERVAL_KEY)        
        self.dbus_client.update_update_interval(interval)

    def wallpaper_callback(self, client, *args, **kwargs):
        wallpaper_directory = self.client.get_string(GCONF_WALLPAPER_KEY)
        self.dbus_client.update_wallpaper_directory(wallpaper_directory)
