import json
from os import name
from hermit_vk_api import *
from hermit_vk_api._vk_api import Resource
import datetime
import time
import math
from tqdm import tqdm
from pathlib import Path

class MessagesPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.id = "_messages"

        self.conversation_by_selection = {}
        self.conversation_by_id = {}
        self.messages = []
        self.message_read_offset = 0
        
        self.selected_conv_id = None

    def get_conversation_by_id(self, id:str):
        id = str(id)
        if id in self.conversation_by_id:
            return self.conversation_by_id[id]
        else:
            convs = self.vk_api.method("messages.getConversationsById", peer_ids=id)['items']
            if len(convs)>0:
                conv = convs[0]
                self.conversation_by_id[id] = conv
                self.setup_conversations([conv])
                return conv

    def setup_conversations(self, convs):
        convs_users = list(filter(lambda x: x['peer']['type']=='user', convs))
        user_ids = list(map(lambda x: str(x['peer']['id']), convs_users))
        self.vk_api.load_profiles(user_ids)

        for conv in convs:
            title = ''
            if conv['peer']['type']=='chat': 
                title = conv['chat_settings']['title']
            if conv['peer']['type']=='user': 
                user = self.vk_api.get_user_profile(conv['peer']['id'])
                title = user['first_name'] + " " + user['last_name']
            conv['title'] = title
    
    def print_message(self, date, peer_id, text):
        user = self.vk_api.get_user_profile(peer_id) if peer_id != 0 else {'last_name': '', 'first_name': 'Me'}
        print(f"--- {user['last_name'] + ' ' + user['first_name']} --- {datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')} --")
        print(f"  {text}")
        print("------------")
    
    def get_conversation_id_by_selection(self, selection):
        if len(selection) <= 3:
            if len(self.conversation_by_selection.keys()) <= 0:
                self._call_command(["browse"])
            else:
                pass
            selection = self.conversation_by_selection[str(selection)]['id']
        return selection
    def get_conversation_id_from_arg(self, conv_arg=None):
        if conv_arg == None: return self.selected_conv_id
        return self.get_conversation_id_by_selection(conv_arg)

    def initialize_commands_decorators(self):

        @register_command(self=self, id='browse',
            help="browse conversations and view messages : 'browse [<count>] [<offset>]'")
        def browse_cmd(count=0, offset=0):
            count = int(count)
            offset = int(offset)
            convs = self.vk_api.method("messages.getConversations", fields='first_name,last_name,name', offset=offset)
            convs = convs["items"]
            if count > 0:
                convs = convs[:count]

            convs = list(map(lambda x: x['conversation'], convs))

            self.setup_conversations(convs)
            
            self.conversation_by_selection = {str(i): conv for i,conv in enumerate(convs)}
            self.conversation_by_id.update({str(conv['peer']['id']): conv for conv in convs})
            
            for i, conv in enumerate(convs[:10]):
                head = string_with_fixed_length(f"[{i}] [ {conv['peer']['id']} ]", 20)
                print(f"{head} {conv['title']}")


        @register_command(self=self, id='chat',
            help="[out of order] enter conversation : 'chat <conv index / conv id>'")
        def chat_cmd(conv_selection=None):
            #TODO: needs reefactor
            peer_id = self.get_conversation_id_from_arg(conv_selection)

            self.selected_conv_id = peer_id
            selected_conv = self.get_conversation_by_id(peer_id)
            self.vk_cli.prompt.set_path(self.id + " | " + clip_text(str(selected_conv['title']), 10))

            peer_id = selected_conv['peer']['id']
            data = self.vk_api.method("messages.getHistory", peer_id=peer_id, count=20)
            self.messages = list(reversed(data['items']))
            self.vk_api.load_profiles( {message['from_id']: 0 for message in self.messages}.keys() )

            for message in self.messages:
                date = message['date']
                text = message['text']
                if len(message['attachments'])>0:
                    text += "\n" + json.dumps(message['attachments'])
                user_id = message['from_id']
                
                self.print_message(date, user_id, text)

        @register_command(self=self, id='send',
            help="send message : ' send \"<message>\" '")
        def send_cmd(message):
            if self.selected_conv_id:
                self.vk_api.method('messages.send', peer_id=self.selected_conv_id, message=message, random_id=0)
                self.print_message(datetime.datetime.now().timestamp(), 0, message)
        
        @register_command(self=self, id='send_raw_attachments',
            help="send raw attachments : ' send \"<attachments>\" '")
        def send_raw_attachment_cmd(*args):
            if self.selected_conv_id:
                attachments = args[:]
                self.vk_api.method('messages.send', peer_id=self.selected_conv_id, message="", random_id=0, attachment=",".join(attachments))
                self.print_message(datetime.datetime.now().timestamp(), 0, ",".join(attachments))

        @register_command(self=self, id='get_members_sites',
            help="help TODO: get members sites : ' get_members_sites [<conv index / conv id>] '")
        def get_members_sites_cmd(selected_conv=None):
            #TODO: needs reefactor
            selected_conv = self.get_conversation_id_from_arg(selected_conv)
            get_profile_pic = False
            
            if selected_conv:
                users_ids = self.vk_api.method('messages.getConversationMembers', peer_id=selected_conv)
                users_ids = users_ids['items']
                users_ids = list(map(lambda x: str(x["member_id"]), users_ids))
                users_ids = list(filter(lambda x: int(x)>0, users_ids))
                users = self.vk_api.method('users.get', user_ids=",".join(users_ids), fields="site,occupation,photo_100")

                column_sizes = [12,30,10,10]

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
                    site_url = ""
                    if "site" in user: 
                        site_url = user["site"].strip()
                    if "occupation" in user:
                        if is_http_url(user["occupation"]['name']): site_url = user["occupation"]['name'].strip()

                    if site_url=="": continue

                    if not "deactivated" in user and not user["is_closed"] \
                        and site_url != "" and is_http_url(site_url) \
                            and not is_execluding(site_url, execludes):
                        
                        line = ""
                        line += string_with_fixed_length(str(user["id"]), column_sizes[0])
                        line += string_with_fixed_length(f"{user['first_name']} {user['last_name']}", column_sizes[1])
                        line += string_with_fixed_length(site_url, column_sizes[2])
                        sites_list_text += line+"  \n"
                
                print(sites_list_text)

        @register_command(self=self, id='compare_names',
            help="help TODO: compare names : ' compare_names <names separated with coma> [<conv index / conv id>]'")
        def compare_names_cmd(names="", selected_conv=None):
            #TODO: needs reefactor
            names = names.split(",")
            selected_conv = self.get_conversation_id_from_arg(selected_conv)

            if selected_conv:
                users_ids = self.vk_api.method('messages.getConversationMembers', peer_id=selected_conv)['items']
                users_ids = list(map(lambda x: str(x["member_id"]), users_ids))
                users_ids = list(filter(lambda x: int(x)>0, users_ids))
                users = self.vk_api.method('users.get', user_ids=",".join(users_ids), fields="site,occupation")
                for user in users:
                    user['similarity'] = 0.0

                for name_index in range(len(names)):
                    sorted_users = user
                    for user in users:
                        first_name = names[name_index].split(" ")[1]
                        last_name = names[name_index].split(" ")[0]

                        #TODO: not finished
        
        @register_command(self=self, id='show_scrolling_message',
            help="sends a message that will be edited and animated as scrolling text : ' show_scrolling_message <message> <title> [<conv index / conv id>]'")
        def show_scrolling_message_cmd(message="с днюхой тебя нахуй, с сорока с чем-то летием блять...", title="", selected_conv=None):
            selected_conv = self.get_conversation_id_from_arg(selected_conv)

            def render_text(title, message, frame=0, length=40):
                text = ""
                text += "🇻🇳"*round((math.sin(frame)+1.5)*3)+"\n"
                text += title+"\n" if title else ""
                message+= "      "
                text += "".join([message[(i+frame*5)%len(message)] for i in range(length)])
                text += "\n"+"🇻🇳"*round((math.sin(-frame)+1.5)*3)
                return text
            
            message_id = self.vk_api.method("messages.send", peer_id=selected_conv, message=render_text(title, message), random_id=0)
            
            for i in range(1, 40):
                time.sleep(1)
                self.vk_api.method("messages.edit", message_id=message_id, peer_id=selected_conv, 
                    message=render_text(title, message, i))

            message_id = self.vk_api.method("messages.delete", peer_id=selected_conv, message_ids=str(message_id), delete_for_all=1)

            # usage:
            # _messages show_scrolling_message "с днюхой тебя нахуй, с сорока с чем-то летием блять... " "Ваня" 344928203


        @register_command(self=self, id='export_attachments',
            help="export all conversation attachments into a <directory>/conversation name : ' export_attachments [<types> : empty - all types, not empty - example: \"photo video audio doc link\"] [<directory>] [<conv index / conv id>]'")
        def export_attachments_cmd(types="photo video audio doc link", directory=None, conv_selection=None):
            if directory==None:
                directory = "~/Downloads/vk exports"

            types = types.split(" ")
            peer_id = self.get_conversation_id_from_arg(conv_selection)
            selected_conv = self.get_conversation_by_id(peer_id)
            dir_path = get_existing_path(directory+"/"+selected_conv['title'])

            all_media = {}

            def gather_all_attachments(peer_id, media_type):
                finished = False
                attachments = []
                start_from = None
                while not finished:
                    result = self.vk_api.method("messages.getHistoryAttachments", 
                        peer_id=peer_id, media_type=media_type, start_from=start_from)
                    attachs = list(map(lambda x: x["attachment"], result["items"]))
                    if len(attachs) > 0:
                        attachments+=(attachs)
                        start_from = result['next_from']
                        time.sleep(0.2)
                    else:
                        finished = True
                        break
                return attachments

            def download_resources(resources:list[Resource], directory=None, pbar_desc=""):
                resources = sorted(resources, key=lambda x: x.date.timestamp() if x.date is not None else 0)
                pbar = tqdm(resources, desc=pbar_desc)
                for resource in pbar:
                    pbar.set_postfix_str(resource.name)
                    resource.download(directory / resource.media_type)

            links = []

            print(f"exported files will be located in folder \"{dir_path.as_posix()}\"")
            
            for media_type in types:
                print(f"exporting attachments with media type '{media_type}'")
                print(f"--- gathering attachments with media type '{media_type}' from peer '{peer_id}' ...")

                attachs = gather_all_attachments(peer_id, media_type)
                resources = list(map(lambda x: Resource.from_attachment(x), attachs))
                all_media[media_type] = resources

                download_resources( 
                    resources, dir_path,
                    pbar_desc=f"--- downloading gathered attachments")

                time.sleep(1)

            Resource.clean_links_file(dir_path/"link")
                