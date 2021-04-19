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
        # print(f"calling {id} with {args}")
        func(args)

    print(f"registering {id}")
    self._commands[id] = wrapper
    self._commands_help[id] = help
        
    return wrapper


class Plugin(object):
    def __init__(self):
        self.id = '_base'
        self.vk_cli : app.VK_CLI = None
        self.vk_api : app.VkSession = None
        self._commands = {}
        self._commands_help = {}
        self.initialize_commands_decorators()
    
    def startup(self):
        print(f"{self.id} plugin loaded")

    # @classmethod
    # def register_command(func, self, id, help="no information", ):
    #     self._commands[id] = func
    #     def _impl(args):
    #         print(f"calling {id} with {args}")
    #         func(args)
    #     return _impl

    def help_print(self, command):
        print( f"  {command} : {self._commands_help[command]}" )

    def _call_command(self, args):
        print()
        if len(args)>0:
            if args[0] == "help":
                if len(args)>1 and args[1] in self._commands_help:
                    self.help_print(args[1])

            elif args[0] in self._commands:
                self._commands[args[0]](args[1:])
        print()

    def initialize_commands_decorators(self):
        pass
