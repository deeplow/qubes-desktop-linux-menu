import subprocess
from gi.repository import GLib

from qubes_tutorial.extensions import (
    GtkTutorialExtension,
    tutorial_register,
    if_tutorial_enabled
)

app_entries_exec_overrides = {} #  "{vm_name}:{app_name}" -> command

def tutorial_override_command_for_vm(get_command_for_vm):
    """
    If the tutorial mode is enabled, it overrides the app exec command when
    """
    @if_tutorial_enabled
    def wrapper(*args, **kwargs):
        app_info = args[0]
        app_name = app_info.app_name
        vm = args[1]
        vm_name = vm.name
        cmd_override = app_entries_exec_overrides.get(f"{vm_name}:{app_name}")
        if cmd_override is not None:
            # call cmd directly and return nop (true)
            tutorial_register("qubes-menu", vm_name, app_name)
            subprocess.Popen(cmd_override, shell=True)
            return ["true"]
        tutorial_register("qubes-menu", vm_name, app_name)
        return get_command_for_vm(*args, **kwargs)
    return wrapper

class QubesMenuTutorialExtension(GtkTutorialExtension):

    def __init__(self, app):
        super().__init__("qubesmenu")
        self.app = app


    def do_show_path_to_app(self, vm_name, app_name):
        """
        Highlights the path to an application, showing the user a path
        to click it.

        :vm_name str:       name of qube
        :app_name str:      name of app
        """
        GLib.idle_add(self.app.show_path_to_app, vm_name, app_name)
        return "highlighted successfully {}, {}".format(vm_name, app_name)

    def do_show_path_to_app_override_exec(self, vm_name, app_name, override_exec):
        """
        Highlights the path to an application, showing the user a path
        to click it. When the user clicks it, it executes instead the commmand
        provided with `override_exec`.

        :override_exec str: executable command to override when user clicks
        """
        global app_entries_exec_overrides
        app_entries_exec_overrides[f"{vm_name}:{app_name}"] = override_exec
        self.do_show_path_to_app(vm_name, app_name)

    def do_remove_highlights(self):
        GLib.idle_add(self.app.clear_path_to_app)

        global app_entries_exec_overrides
        app_entries_exec_overrides.clear()

        return "removed highlights"
