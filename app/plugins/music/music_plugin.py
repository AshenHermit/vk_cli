from app import *
import datetime

class Music(Plugin):
    def __init__(self):
        super().__init__()
        self.id = "_music"

    def initialize_commands_decorators(self):
        @register_command(self=self, id='cmd',
            help="cmd : 'cmd'")
        def cmd_cmd(args):
            pass