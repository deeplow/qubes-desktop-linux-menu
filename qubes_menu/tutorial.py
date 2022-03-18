import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from gi.repository import GLib

import qubes_tutorial.interactions as interactions

tutorial_enabled = False
menu_app = None

def enable_menu_tutorial(app):
    """
    Enables menu logic to communicate with the qubes tutorial component
    """
    global tutorial_enabled
    tutorial_enabled = True
    global menu_app
    menu_app = app

    DBusGMainLoop(set_as_default=True)
    TutorialDBUSService(app)

def tutorial_register_decorator(interaction_name):
    """
    If the tutorial mode is enabled, it informs the tutorial of these calls
    """
    def tutorial_register_decorator(func):
        def wrapper(*args):
            func(*args)
            if tutorial_enabled:
                interactions.register(interaction_name)
        return wrapper
    return tutorial_register_decorator

def tutorial_register(name: str, subject: str="", arguments: str=""):
    if tutorial_enabled:
        interactions.register(name, subject, arguments)

class TutorialDBUSService(dbus.service.Object):
    """
    Listen to tutorial instructions
    """
    def __init__(self, app):
        self.app = app
        bus_name = dbus.service.BusName("org.qubes.tutorial.qubesmenu",
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/qubes/tutorial/qubesmenu')

    @dbus.service.method('org.qubes.tutorial.qubesmenu')
    def show_path_to_app(self, vm_name, app_name):
        """
        Highlights the path to an application, showing the user a path
        to click it.

        :vm_name str:       name of qube
        :app_name str:      name of app
        """

        GLib.idle_add(self.app.show_path_to_app, vm_name, app_name)
        return "highlighted successfully {}, {}".format(vm_name, app_name)

    @dbus.service.method('org.qubes.tutorial.qubesmenu')
    def remove_highlights(self):
        GLib.idle_add(self.app.clear_path_to_app)
        return "removed highlights"
