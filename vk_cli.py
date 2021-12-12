import argparse

from oauthlib import oauth2
import oauthlib
from oauthlib import common

from launcher_modules import *
import oauthlib.oauth2
import oauthlib.common

VERSION = 0.01

def main():
    launcher = Launcher()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", nargs='?', default='run')
    args = parser.parse_args()

    launcher.start(args.operation)

# def main():
#          = oauth2.ImplicitGrant(oauth2.RequestValidator())
#     request = common.Request("https://oauth.vk.com/authorize?client_id=7934023&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=docs&response_type=token&v=5.131")
#     def token_handler(token):
#         print(token)
#     implgrant.create_authorization_response(
#         request,
#         token_handler
#     )
    

if __name__ == '__main__':
    main()