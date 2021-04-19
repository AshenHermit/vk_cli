import argparse

from launcher_modules import *

VERSION = 0.01

def main():
    launcher = Launcher()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", nargs='?', default='run')
    args = parser.parse_args()

    launcher.start(args.operation)
    

if __name__ == '__main__':
    main()