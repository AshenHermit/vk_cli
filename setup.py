from setuptools import setup, find_packages
from pathlib import Path
 
def get_requirements():
    requirements_path = (Path(__file__)/'../requirements.txt').resolve()
    requirements = requirements_path.read_text(encoding='utf-8')
    requirements = requirements.split("\n")
    requirements = list(map(lambda x: x.strip(), requirements))
    return requirements

setup(
    name='vk_cli',
    version='0.3',
    description='A small application for executing Python scripts with access to the VK api at the user level.',
    author='hermit',
    author_email='nameless.voice.x@gmail.com',
    packages = find_packages(exclude=["launcher_modules"]),
    install_requires = ["setuptools", "pathlib"],
    requires = get_requirements(),
    entry_points = {
        'console_scripts': [
            'vk-cli = vk_cli.run_vk_cli:main',
        ],
    },
)