import os
import importlib
from functools import partial, wraps
import app

def load_plugins(directory, vk_cli, vk_api):
    dir_list = os.listdir(directory)
    plugins = []
    
    for s in dir_list:
        s = directory + '/' + s
        module_name = s.replace('/', '.')
        try:
            if os.path.isdir(s):
                importlib.import_module(module_name)
        except ModuleNotFoundError:
            print(f"no module '{s}'")


    for plugin_class in Plugin.__subclasses__():
        plugin = plugin_class()
        plugin.vk_api = vk_api
        plugin.vk_cli = vk_cli
        plugins.append(plugin)

    return plugins


def register_command(func=None, self=None, id='_', help='no information'):
    if func is None:
        return partial(register_command, self=self, id=id, help=help)

    @wraps(func)
    def wrapper(args):
        func(args)

    self._commands[id] = wrapper
    self._commands_help[id] = help
        
    return wrapper


class CommandAgent():
    def __init__(self):
        self._commands = {}
        self._commands_help = {}
        self.initialize_commands_decorators()
    
    def _help_print(self, command):
        print( f"  {command} : {self._commands_help[command]}" )

    def _call_command(self, args):
        print()
        try:
            if len(args)>0:
                if args[0] == "help" and len(args)>1 and args[1] in self._commands_help:
                    self._help_print(args[1])
                    return

                elif args[0] in self._commands:
                    self._commands[args[0]](args[1:])

        except Exception as err:
            # raise err
            print(f"[COMMAND EXECUTION ERROR] {err}")

        print()

    def initialize_commands_decorators(self):
        pass



class Plugin(CommandAgent):
    def __init__(self):
        self.id = '_base'
        self.vk_cli : app.VK_CLI = None
        self.vk_api : app.VkSession = None

        super().__init__()
    
    def startup(self):
        print(f"{self.id} plugin loaded")
    
