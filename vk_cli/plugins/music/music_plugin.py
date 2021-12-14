from vk_cli import *
import datetime
import m3u8

class Music(Plugin):
    def __init__(self):
        super().__init__()
        self.id = "_music"

    def initialize_commands_decorators(self):

        @register_command(self=self, id='download',
            help="download music file : 'download <audio id>'")
        def cmd_cmd(args):
            pass