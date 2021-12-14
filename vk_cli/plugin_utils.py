import os
import importlib
from functools import partial, wraps
from pathlib import Path
import vk_cli
import traceback
import sys
import inspect
import operator

def get_plugins_in_module(module):
    def attr_is_plugin_class(attr):
        if attr is Plugin: return False
        if not inspect.isclass(attr): return False
        return Plugin in inspect.getmro(attr)

    mdict = module.__dict__
    subclasses = list(map(lambda k: mdict[k], list(mdict.keys())))
    subclasses = list(filter(attr_is_plugin_class, subclasses))
    return subclasses

def load_plugins(plugins_directory:Path, app_directory:Path, vk_cli, vk_api):
    dir_list = os.listdir(plugins_directory)
    plugins = []
    
    plugin_classes = []
    for s in dir_list:
        relative_path = plugins_directory.as_posix()[len((app_directory/'..').resolve().as_posix())+1:]
        s = relative_path + '/' + s
        module_name = s.replace('/', '.')

        try:
            if s.find(".")==-1:
                if module_name in sys.modules:
                    for k in list(sys.modules.keys()):
                        if k.startswith(module_name):
                            importlib.reload(sys.modules.get(k))
                module = importlib.import_module(module_name)
                plugin_classes += get_plugins_in_module(module)
        except ModuleNotFoundError:
            print(f"no module '{module_name}' '{s}'")
        except:
            traceback.print_exc()
            

    for plugin_class in plugin_classes:
        plugin = plugin_class()
        plugin.vk_api = vk_api
        plugin.vk_cli = vk_cli
        plugins.append(plugin)

    return plugins


def register_command(func=None, self=None, id='_', help='no information'):
    if func is None:
        return partial(register_command, self=self, id=id, help=help)

    @wraps(func)
    def wrapper(*args):
        func(*args)

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
                    args_tuple = tuple(args[1:])
                    self._commands[args[0]](*args_tuple)
        
        except Exception as err:
            # raise err
            print(f"[COMMAND EXECUTION ERROR] {err}")
            traceback.print_exc()

        print()

    def initialize_commands_decorators(self):
        pass

class Plugin(CommandAgent):
    def __init__(self):
        self.id = '_base'
        self.vk_cli : vk_cli.VK_CLI = None
        self.vk_api : vk_cli.VkSession = None

        super().__init__()
    
    def startup(self):
        print(f"{self.id} plugin loaded")
    
