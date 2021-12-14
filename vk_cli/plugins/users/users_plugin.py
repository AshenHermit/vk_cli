from vk_cli import *

class UsersPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.id = "_users"


    def get_ids(self, args):
        args = list(map(lambda arg: arg[arg.rfind('/')+1:] if arg[:len('https://')] == 'https://' else arg, args))
        return args
    
    def print_user(self, user):
        print(f"[ {user['id']} ][ {user['screen_name']} ][ {user['last_name']} {user['first_name']} ]")

    def initialize_commands_decorators(self):
        
        @register_command(self=self, id="get", 
            help="get user information 'get <user_id / url / screen_name> ...'")
        def get_cmd(args):
            if len(args) == 0:
                self._help_print('get')
                return

            ids = self.get_ids(args)
            self.vk_api.load_profiles(ids)

            for id in ids:
                user = self.vk_api.get_user_profile(id)
                self.print_user(user)


        @register_command(self=self, id="mutual_friends", 
            help="get mutual friends of users 'mutual_friends <user_id / url / screen_name> ...'")
        def mutual_friends_cmd(args):
            if len(args) == 0:
                self._help_print('mutual_friends')
                return

            ids = self.get_ids(args)
            self.vk_api.load_profiles(ids)
            ids = list(map(lambda id: self.vk_api.get_user_profile(id)['id'], ids))
            separated_friends_ids = list(map( lambda user_id:
                                            self.vk_api.method('friends.get', user_id=user_id)['items'],
                                        ids))
            
            friends = list({inner: 0 for outer in separated_friends_ids for inner in outer}.keys())
            def is_friend_of_all_users(friend_id):
                result = True
                for i in range(len(ids)):
                    result = result and (friend_id in separated_friends_ids[i])
                return result

            friends = list(filter(is_friend_of_all_users, friends))
            self.vk_api.load_profiles(friends)

            for id in friends:
                user = self.vk_api.get_user_profile(id)
                self.print_user(user)