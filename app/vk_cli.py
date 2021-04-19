from cmd import Cmd
import json
from pathlib import Path
from app._vk_api import VkSession, invalid_password
from app.plugin_utils import load_plugins
import re

class Prompt(Cmd):
    def __init__(self, on_input):
        self.prompt_prefix = 'vk_cli'
        self.prompt_postfix = '> '
        self.set_path("")

        self.on_input = on_input

        super(Prompt, self).__init__()

    def set_path(self, path):
        self.prompt = self.prompt_prefix + ("" if path=="" else " ") + path + self.prompt_postfix

    def text_to_args(self, text):
        break_indices = []
        pat = re.compile(r'".*?"')
        match = pat.search(text)
        args = []
        while match:
            span = match.span()
            break_indices.append(span[0])
            break_indices.append(span[1])

            match = pat.search(text, break_indices[-1])

        spaces = [m.start() for m in re.finditer(' ', text)]
        space_indices = []
        for space_idx in spaces:
            is_in_quotes = False
            for i in range(len(break_indices)//2):
                if space_idx > break_indices[i*2] and space_idx < break_indices[i*2+1]:
                    is_in_quotes = True
            
            if not is_in_quotes: space_indices.append(space_idx)

        break_indices = list(sorted(break_indices+space_indices))

        last_break_index = 0
        for break_index in break_indices:
            args.append(text[last_break_index : break_index])
            last_break_index = break_index
        args.append(text[last_break_index:])

        for i in range(len(args)):
            if args[i].find('"') == -1:
                for j in range(4):
                    args[i] = args[i].replace(" ", "")
            args[i] = args[i].replace('"', '')

        args = list(filter(lambda x: x!="", args))

        return args

    def default(self, inp):
        args = self.text_to_args(inp)
        self.on_input(args)

    def do_help(self, inp):
        self.default("help " + inp)
        # print("for plugin help print '? <command>'")
        
    def do_exit(self, inp):
        return True

class VK_CLI():
    def __init__(self):
        print("initializng vk cli...")

        self.prompt = Prompt(self.on_input)

        self.vk_api : VkSession = None
        self.users = {}

        self.settings_file_path = "settings.json"
        self.settings = {
            'plugins_path': 'app/plugins'
        }

        self.plugins = []
        self.plugin_by_id = {}

        self.last_used_plugin_id = ""

    def start(self):
        self.load_settings()
        self.startup_log_in()

        try: self.prompt.cmdloop()
        except KeyboardInterrupt:
            print("[Keyboard Interrupt]")

    def load_profiles(self, ids):
        users = self.vk_api.method('users.get', user_ids=",".join(list(map(lambda x: str(x), ids))))
        for user in users:
            self.users[str(user['id'])] = user

    def get_user_profile(self, id):
        id = str(id)
        if id not in self.users:
            self.load_profiles([id])
        return self.users[id]

    def load_settings(self):
        settings_path = Path(self.settings_file_path)

        if settings_path.exists():
            loaded_settings = json.loads(settings_path.read_text())
            if loaded_settings:
                z = self.settings.copy()
                z.update(loaded_settings)
                self.settings = z

        self.save_settings()

    def load_plugins(self):
        if self.vk_api:
            self.plugins = load_plugins(self.settings['plugins_path'], self, self.vk_api)
            for plugin in self.plugins:
                self.plugin_by_id[plugin.id] = plugin
                

    def save_settings(self):
        settings_path = Path(self.settings_file_path)
        settings_path.write_text(json.dumps(self.settings))

    def startup_log_in(self):
        if 'email' in self.settings and 'password' in self.settings:
            self.log_in(self.settings['email'], self.settings['password'], )

    def log_in(self, email, password, load_plugins=True):
        self.settings['email'] = email
        self.settings['password'] = password
        try:
            self.vk_api = VkSession(self.settings['email'], self.settings['password'])
        except invalid_password:
            return "invalid authorization"

        self.save_settings()
        self.load_plugins()
        return "successfully authorized"

    def help_print(self):
        print()
        print("plugins list:")
        for plugin in self.plugins:
            print(f"  {plugin.id}")

        if self.last_used_plugin_id:
            print()
            print(f"{self.last_used_plugin_id} commands list:")
            last_plugin = self.plugin_by_id[self.last_used_plugin_id]
            for command_id in last_plugin._commands.keys():
                last_plugin.help_print(command_id)
        
        print()


    def prompt_input(self, args):
        if len(args)>0:
            if args[0] == "..":
                self.prompt.set_path("")
                self.last_used_plugin_id = None

            elif args[0] == "help":
                self.help_print()

            elif args[0] in self.plugin_by_id:
                self.last_used_plugin_id = args[0]
                self.plugin_by_id[args[0]]._call_command(args[1:])
                self.prompt.set_path(self.last_used_plugin_id)

            elif self.last_used_plugin_id in self.plugin_by_id:
                self.plugin_by_id[self.last_used_plugin_id]._call_command(args[:])

                

    def unauthorized_input(self, args):
        if args[0] == "login":
            if len(args) == 3:
                message = self.log_in(args[1], args[2])
                print(message)
                return
        
        print("please, log in with command 'login <email/phone> <password>'")

        
    def on_input(self, args):
        if self.vk_api:
            self.prompt_input(args)
        else:
            self.unauthorized_input(args)
        
