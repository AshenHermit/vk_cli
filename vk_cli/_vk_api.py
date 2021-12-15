from datetime import datetime
from pathlib import Path
import requests
import lxml.html
import json
import re
import time
import urllib.parse
from selenium.webdriver import Chrome
from vk_api.vk_api import VkApi
import traceback
import os

from vk_cli.utils import get_extension_from_url, make_dirs, normalize_filepath_name

class invalid_password(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)

class not_valid_method(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)

class user_is_not_authorized(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)

MEDIA_EXTENSIONS = {"photo": "jpg", "video": "mp4", "audio": "mp3"}

class Resource:
    name:str = ""
    description:str = ""
    url:str = ""
    media_type:str = ""
    extension:str = ""
    date:datetime = None

    def download_from_url(self, directory:Path):
        ext = self.extension
        if ext=="":
            ext = get_extension_from_url(self.url)
            if ext=="":
                ext = MEDIA_EXTENSIONS[self.media_type]

        name = self.name.replace(".", "_")
        filepath = Path(directory) / (name+"."+ext)
        filepath = normalize_filepath_name(filepath)

        make_dirs(filepath)

        if self.url.find("http")==-1: return
        if filepath.exists(): return

        retries = 4
        while retries>0:
            try:
                response = requests.get(self.url, stream=True)
                retries = 0
                break
            except:
                retries-=1

        try:
            file = filepath.open("wb")
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
            file.close()

            modTime = time.mktime(self.date.timetuple())
            os.utime(str(filepath), (modTime, modTime))
        except:
            traceback.print_exc(1)


    def save_link(self, directory:Path):
        data = {"date": self.date.ctime() if self.date is not None else None, "url": self.url}
        filepath = directory/"links.json"
        if not filepath.exists():
            make_dirs(filepath)
            links = [data]
        else:
            links = json.loads(filepath.read_text(encoding='utf-8'))
            links.append(data)
        filepath.write_text(json.dumps(links, indent=2, ensure_ascii=False), encoding='utf-8')

    def download(self, directory:Path):
        try:
            if self.media_type == "link":
                self.save_link(directory)
            else:
                self.download_from_url(directory)
        except:
            traceback.print_exc(1)

    @staticmethod
    def clean_links_file(directory:Path):
        filepath = directory/"links.json"
        if filepath.exists():
            links = json.loads(filepath.read_text(encoding='utf-8'))
            link_by_url = {ln['url']: ln for ln in links}
            links = list(link_by_url.values())
            filepath.write_text(json.dumps(links, indent=2, ensure_ascii=False), encoding='utf-8')
        
    @staticmethod
    def from_photo(data:dict):
        res = Resource()
        id = f'{data["owner_id"]}_{data["id"]}'
        res.name = id
        res.date = datetime.fromtimestamp(data['date'])
        res.url = sorted(data['sizes'], key=lambda x: x['height']*x['width'])[-1]['url']
        res.extension = get_extension_from_url(res.url)
        res.media_type = "photo"
        return res

    @staticmethod
    def from_video(data:dict):
        res = Resource()
        id = f'{data["owner_id"]}_{data["id"]}'
        res.name = id
        res.date = datetime.fromtimestamp(data['date'])

        if not "files" in data: return res
        
        files = data["files"]
        if "external" in files:
            res.media_type = "link"
            res.url = files["external"]
        else:
            res.media_type = "video"
            prev_size = 0
            for key in files.keys():
                if key.startswith("mp4"):
                    size = prev_size
                    try:
                        size = int(re.search(r"_([^\D]+)", key).group(1))
                    except: pass
                    if size >= prev_size:
                        res.url = files[key]
                    prev_size = size
            res.extension = "mp4"
        return res

    @staticmethod
    def from_audio(data:dict):
        res = Resource()
        id = f'{data["owner_id"]}_{data["id"]}'
        res.name = f'{data["artist"]} - {data["title"]} - {id}'
        res.date = datetime.fromtimestamp(data['date'])
        res.url = data['url']
        res.extension = "mp3"
        res.media_type = "audio"
        return res

    @staticmethod
    def from_doc(data:dict):
        res = Resource()
        id = f'{data["owner_id"]}_{data["id"]}'
        res.name = f'{data["title"].replace(".", "_")} - {id}'
        res.date = datetime.fromtimestamp(data['date'])
        res.url = data['url']
        res.extension = data['ext']
        res.media_type = "doc"
        return res
    
    @staticmethod
    def from_link(data:dict):
        res = Resource()
        res.name = f'{data["title"]}'
        res.url = data['url']
        res.media_type = "link"
        return res

    @staticmethod
    def from_attachment(attach:dict):
        attach_type = attach["type"]
        attach = attach[attach_type]
        constructors = {}
        constructors["photo"] = Resource.from_photo
        constructors["video"] = Resource.from_video
        constructors["audio"] = Resource.from_audio
        constructors["doc"] = Resource.from_doc
        constructors["link"] = Resource.from_link
        if attach_type in constructors:
            try:
                res = constructors[attach_type](attach)
                return res
            except:
                traceback.print_exc(1)
                
        return Resource()    
    
class VkSession(object):
    def __init__(self, login, password, chromedriver_path="chromedriver/chromedriver.exe"):
        self.login = login
        self.password = password
        self.vk_session = None
        self.users = {}
        self.chromedriver_path = chromedriver_path

        self.app_id = 6121396 # vk admin
        self.scope = 1073737727

        self.auth()

    def get_token_with_implicit_flow(self):
        # 1073737727
        executable_path = (Path(__file__) / ("../"+self.chromedriver_path)).resolve()
        # 'chromedriver.exe' executable needs to be in PATH. Please see https://sites.google.com/a/chromium.org/chromedriver/home
        driver = Chrome()
        app_id = self.app_id
        scope = self.scope
        url = f"https://oauth.vk.com/authorize?client_id={app_id}&scope={scope}&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1"
        driver.get(url)
        inputs = driver.find_elements_by_class_name("oauth_form_input")
        inputs[0].send_keys(self.login)
        inputs[1].send_keys(self.password)
        driver.find_element_by_class_name("oauth_button").click()
        driver.find_element_by_class_name("button_indent").click()
        access_token = urllib.parse.parse_qs(urllib.parse.urlsplit(driver.current_url).fragment)["access_token"][0]
        driver.close()

        return access_token

    def get_vk_config_path(self):
        filepath = (Path(__file__) / '../../vk_config.v2.json').resolve()
        return filepath

    def get_token_from_vk_config(self):
        filepath = self.get_vk_config_path()
        if not filepath.exists(): return None
        try:
            with filepath.open("r", encoding="utf-8") as file:
                config = json.load(file)
            app_key = f"app{self.app_id}"
            app = config[self.login]["token"][app_key]
            scopes = list(app.values())
            return scopes[0]["access_token"]
        except:
            traceback.print_exc()
            print("removing vk config file")
            os.remove(filepath.as_posix())
        return None

    def auth(self):
        print("authorizing...")
        access_token = self.get_token_from_vk_config()
        if access_token is None:
            access_token = self.get_token_with_implicit_flow()

        self.vk_session = VkApi(
            login=self.login, password=self.password, 
            app_id=self.app_id, token=access_token, 
            captcha_handler=self.captcha_handler, 
            config_filename = self.get_vk_config_path())
        
        try:
            self.vk_session.auth()
            print(f"vk config located in \"{self.get_vk_config_path().as_posix()}\"")
        except Exception as e:
            traceback.print_exc()
            self.vk_session = None
    
    def method(self, method, v='5.131', **params):
        if self.vk_session is None:
            raise user_is_not_authorized("vk_session is None")
        
        result = self.vk_session.method(method, params)
        return result

    def captcha_handler(self, captcha):
        """ При возникновении капчи вызывается эта функция и ей передается объект
            капчи. Через метод get_url можно получить ссылку на изображение.
            Через метод try_again можно попытаться отправить запрос с кодом капчи
        """
        
        key = input("\nEnter captcha code {0}: ".format(captcha.get_url())).strip()

        return captcha.try_again(key)

    def load_profiles(self, ids:list[int] or list[str]):
        ids = list(filter(lambda id: id not in self.users, ids))
        if len(ids)>0:
            users = self.method('users.get', user_ids=",".join(list(map(lambda x: str(x), ids))), extended=1, fields='screen_name,photo_max_orig,photo_id')
            photos = []
            try:
                photo_ids = list(map(lambda x: x['photo_id'] if 'photo_id' in x else "344928203_457259835", users))
                photos = self.method("photos.getById", photos=",".join(photo_ids))
            except:
                pass

            
            for i,user in enumerate(users):
                self.users[str(user['id'])] = user
                if 'deactivated' in user: 
                    user['screen_name'] = 'id'+str(user['id'])
                photo_res = Resource.from_photo(photos[i])
                user['photo_url'] = photo_res.url
                self.users[str(user['screen_name'])] = user


    def get_user_profile(self, id:int or str):
        id = str(id)
        if id not in self.users:
            self.load_profiles([id])
        return self.users[id]

class VkSessionOld(object):
    def __init__(self,login,password):
        self.login = login
        self.password = password
        self.hashes = {}
        self.auth()

        self.users = {}
        
    def auth(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Connection':'keep-alive',
            'DNT':'1'}
        self.session = requests.session()
        data = self.session.get('https://vk.com/', headers=headers)
        page = lxml.html.fromstring(data.content)
        form = page.forms[1]
        form.fields['email'] = self.login
        form.fields['pass'] = self.password
        response = self.session.post(form.action, data=form.form_values())
        if "onLoginDone" not in response.text: raise invalid_password("invalid password!")
        return

    def method(self,method,v='5.131',**params):
        if method not in self.hashes:
            self._get_hash(method)
        data = {'act': 'a_run_method','al': 1,
                'hash': self.hashes[method],
                'method': method,
                'param_v':v}
        for i in params:
            data["param_"+i] = params[i]
        answer = self.post_act('https://vk.com/dev', 'a_run_method', data)
        res = None
        res = json.loads(answer[0])
        if "error" in res:
            raise Exception(res['error'])
        res = res['response']
        return res
    
    def _get_hash(self, method=""):
        if not method: return ""
        success = False
        html = None
        while not success:
            try: 
                html = self.session.get('https://vk.com/dev/' + method)
                success = True
            except:
                pass

        time.sleep(0.1)
        hash_0 = re.findall('onclick="Dev.methodRun\(\'(.+?)\', this\);', html.text)
        if len(hash_0)==0:
            raise not_valid_method("method is not valid")
        self.hashes[method] = hash_0[0].replace(":", "_")
        return self.hashes[method]

    def post_act(self, url, act, data, method=""):
        data['al'] = 1
        data['act'] = act
        data['hash'] = self._get_hash(method)
        res = self.session.post(url, data=data)
        if res:
            result = res.text.replace("<!--", "", 1)
            result = json.loads(result)['payload'][-1]
            return result

    def load_profiles(self, ids):
        ids = list(filter(lambda id: id not in self.users, ids))
        if len(ids)>0:
            users = self.method('users.get', user_ids=",".join(list(map(lambda x: str(x), ids))), extended=1, fields='screen_name')
            for user in users:
                self.users[str(user['id'])] = user
                if 'deactivated' in user: 
                    user['screen_name'] = 'id'+str(user['id'])
                self.users[str(user['screen_name'])] = user

    def get_user_profile(self, id):
        id = str(id)
        if id not in self.users:
            self.load_profiles([id])
        return self.users[id]


