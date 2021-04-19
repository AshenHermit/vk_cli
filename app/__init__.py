from app.vk_cli import VK_CLI
from app._vk_api import VkSession
from app.plugin_utils import *
from app.utils import *

def run():
    cli = VK_CLI()
    cli.start()