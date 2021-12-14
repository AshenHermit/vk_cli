from vk_cli import *
import datetime

class Docs(Plugin):
    def __init__(self):
        super().__init__()
        self.id = "_docs"

    def initialize_commands_decorators(self):
        @register_command(self=self, id='upload_graffity',
            help="upload_graffity : 'smth'")
        def cmd_upload_graffity(args):
            data = self.vk_api.post_act("https://vk.com/docs.php", "a_save_doc", )
            print(data)