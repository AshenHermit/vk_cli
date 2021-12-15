from sys import argv
from vk_cli import run

def main():
    command = None
    if len(argv)>1:
        command = argv[1]
    run(command)

if __name__ == '__main__':
    main()