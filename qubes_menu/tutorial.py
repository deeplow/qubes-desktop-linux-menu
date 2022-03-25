import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import subprocess

from gi.repository import GLib

import qubes_tutorial.interactions as interactions

tutorial_enabled = False
menu_app = None
app_entries_exec_overrides = {} #  "{vm_name}:{app_name}" -> command

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

def tutorial_modify_command_for_vm(get_command_for_vm):
    """
    If the tutorial mode is enabled, it overrides the app exec command when
    """
    def wrapper(*args, **kwargs):
        app_info = args[0]
        app_name = app_info.app_name
        vm = args[1]
        vm_name = vm.name
        if tutorial_enabled:
            cmd_override = app_entries_exec_overrides.get(f"{vm_name}:{app_name}")
            if cmd_override is not None:
                # call cmd directly and return nop (true)
                tutorial_register("qubes-menu", vm_name, app_name)
                subprocess.Popen(cmd_override, shell=True)
                return ["true"]
            tutorial_register("qubes-menu", vm_name, app_name)
        return get_command_for_vm(*args, **kwargs)
    return wrapper

class TutorialDBUSService(dbus.service.Object):
    """
    Listen to tutorial instructions
    """
    def __init__(self, app):
        self.app = app
        bus_name = dbus.service.BusName("org.qubes.tutorial.extensions",
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/qubesmenu')

    @dbus.service.method('org.qubes.tutorial.extensions')
    def show_path_to_app(self, vm_name, app_name, override_exec):
        """
        Highlights the path to an application, showing the user a path
        to click it.

        :vm_name str:       name of qube
        :app_name str:      name of app
        :override_exec str: executable command to override when user clicks
        """

        if override_exec != "":
            global app_entries_exec_overrides
            app_entries_exec_overrides[f"{vm_name}:{app_name}"] = override_exec

        GLib.idle_add(self.app.show_path_to_app, vm_name, app_name)
        return "highlighted successfully {}, {}".format(vm_name, app_name)

    @dbus.service.method('org.qubes.tutorial.extensions')
    def remove_highlights(self):
        GLib.idle_add(self.app.clear_path_to_app)

        global app_entries_exec_overrides
        app_entries_exec_overrides.clear()

        return "removed highlights"
