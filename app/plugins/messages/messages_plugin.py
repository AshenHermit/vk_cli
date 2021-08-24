import json
from app import *
import datetime

class MessagesPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.id = "_messages"

        self.conversations = []
        self.conversation_by_id = {}
        self.messages = []
        self.message_read_offset = 0
        
        self.selected_conv_id = None

    def print_message(self, date, peer_id, text):
        user = self.vk_api.get_user_profile(peer_id) if peer_id != 0 else {'last_name': '', 'first_name': 'Me'}
        print(f"--- {datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')} --- {user['last_name'] + ' ' + user['first_name']} --")
        print(f"  {text}")
        print("------------")

    def initialize_commands_decorators(self):

        @register_command(self=self, id='browse',
            help="browse conversations and view messages : 'browse'")
        def browse_cmd(args):
            self.conversations = self.vk_api.post_act('https://vk.com/al_im.php?act=a_dialogs_preload', 'a_dialogs_preload', {})
            self.conversations = self.conversations[0]
            self.conversations = list(map(lambda x: {'id': x[0], 'title': x[1]}, self.conversations))
            self.conversation_by_id = {conv['id']: conv for conv in self.conversations}
            
            for i, conv in enumerate(self.conversations[:10]):
                head = string_with_fixed_length(f"[{i}] [ {conv['id']} ]", 20)
                print(f"{head} {conv['title']}")


        @register_command(self=self, id='chat',
            help="enter conversation : 'chat <conv index / conv id>'")
        def read_cmd(args):
            if len(args)==0:
                self._help_print('chat')
                return

            selected_conv = int(args[0])
            if len(str(selected_conv)) <= 3:
                if len(self.conversations) < 1: 
                    self._call_command(["browse"])
                selected_conv = self.conversations[selected_conv]['id']

            self.selected_conv_id = selected_conv
            selected_conv = self.conversation_by_id[self.selected_conv_id]

            self.vk_cli.prompt.set_path(self.id + " | " + clip_text(str(selected_conv['title']), 10))

            self.messages = self.vk_api.post_act('https://vk.com/al_im.php?act=a_start', 'a_start', 
                {'im_v': 3, 'gid': 0, 'block': True, 'history': True, 'msgid': False, 'peer': selected_conv['id']})
            self.messages = list(self.messages[0]['msgs'].keys())
            self.messages = self.vk_api.method('messages.getById', message_ids=','.join(self.messages), extended=1, fields='first_name,last_name')['items']
            self.vk_api.load_profiles( {message['from_id']: 0 for message in self.messages}.keys() )

            for message in self.messages:
                date = message['date']
                text = message['text'] + "\n" + json.dumps(message['attachments'])
                user_id = message['from_id']
                
                self.print_message(date, user_id, text)

        @register_command(self=self, id='send',
            help="send message : ' send \"<message>\" '")
        def send_cmd(args):
            if self.selected_conv_id:
                message = args[0]
                self.vk_api.method('messages.send', peer_id=self.selected_conv_id, message=message, random_id=0)
                self.print_message(datetime.datetime.now().timestamp(), 0, message)
        
        @register_command(self=self, id='send_raw_attachments',
            help="send raw attachments : ' send \"<attachments>\" '")
        def send_raw_attachment_cmd(args):
            if self.selected_conv_id:
                attachments = args[:]
                self.vk_api.method('messages.send', peer_id=self.selected_conv_id, message="", random_id=0, attachment=",".join(attachments))
                self.print_message(datetime.datetime.now().timestamp(), 0, ",".join(attachments))

        @register_command(self=self, id='get_members_sites',
            help="help TODO: get members sites : ' get_members_sites '")
        def get_members_sites_cmd(args):
            if self.selected_conv_id:
                users_ids = self.vk_api.method('messages.getConversationMembers', peer_id=self.selected_conv_id)['items']
                users_ids = list(map(lambda x: str(x["member_id"]), users_ids))
                users_ids = list(filter(lambda x: int(x)>0, users_ids))
                users = self.vk_api.method('users.get', user_ids=",".join(users_ids), fields="site")

                column_sizes = [12,30,10]

                sites_list_text = f"{len(users)} members" 
                sites_list_text += "\n" 
                sites_list_text += string_with_fixed_length(f"vk id", column_sizes[0]) 
                sites_list_text += string_with_fixed_length(f"name", column_sizes[1]) 
                sites_list_text += string_with_fixed_length(f"site", column_sizes[2]) 
                sites_list_text += "  \n" 

                execludes = ["instagram.", "/vk.com/", "/t.me/", "/steamcommunity.com/", "/yummyanime.club/", "/prostobank.", ]
                def is_execluding(text, execludes):
                    for exec in execludes:
                        if text.find(exec)!=-1: return True
                    return False

                for user in users:
                    if not "site" in user: continue

                    site_url = user["site"].strip()
                    if not "deactivated" in user and not user["is_closed"] \
                        and site_url != "" and site_url[0:4] == "http" \
                            and not is_execluding(site_url, execludes):
                        
                        line = ""
                        line += string_with_fixed_length(str(user["id"]), column_sizes[0])
                        line += string_with_fixed_length(f"{user['first_name']} {user['last_name']}", column_sizes[1])
                        line += string_with_fixed_length(site_url, column_sizes[2])
                        sites_list_text += line+"  \n"
                
                print(sites_list_text)
