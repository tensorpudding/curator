import dbus
import gtk
import appindicator
import threading

import backend

DBUS_OBJECT = 'org.curator'
DBUS_PATH = '/org/curator'
DBUS_INTERFACE = 'org.curator'

if __name__=='__main__':
    backend.DBusThread().start()

    bus = dbus.SessionBus()
    try:
        remote = bus.get_object(DBUS_OBJECT, DBUS_PATH)
    except:
        sys.exit(1)
    iface = dbus.Interface(remote, DBUS_INTERFACE)

    # Get config file from builder file
    builder = gtk.Builder()
    builder.add_from_file("curator.glade")
    
    # Construct GUI
    ind = appindicator.Indicator("curator",
                                 CURATOR_ICON,
                                 appindicator.CATEGORY_APPLICATION_STATUS)
    ind.set_status(appindicator.STATUS_ACTIVE)
    
    menu = gtk.Menu()
    ind.set_menu(menu)

    # Enter loop
    gtk.main()
