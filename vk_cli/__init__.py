from vk_cli.vk_cli import VK_CLI
from vk_cli._vk_api import VkSession
from vk_cli.plugin_utils import *
from vk_cli.utils import *

def run(command=None):
    cli = VK_CLI()
    cli.start(command)