import dbus
import dbus.service

import qubes_tutorial.interactions as interactions

def tutorial_register(interaction_name):
    """
    If the tutorial mode is inabled, it informs the tutorial of these calls
    """
    def tutorial_register_decorator(func):
        def wrapper(*args):
            self = args[0]
            func(*args)
            if self.tutorial_enabled:
                interactions.register(interaction_name)
        return wrapper
    return tutorial_register_decorator

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
        def on_complete():
            interactions.register("tutorial:next")
            self.app.clear_path_to_app()
        self.app.show_path_to_app(vm_name, app_name, on_complete)
        return "highlighted successfully {}, {}".format(vm_name, app_name)
