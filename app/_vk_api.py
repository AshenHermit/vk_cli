import requests
import lxml.html
import json
import re
import time

class invalid_password(Exception):
    def __init__(self, value): self.value = value
    def __str__(self):return repr(self.value)

class not_valid_method(Exception):
    def __init__(self, value): self.value = value
    def __str__(self):return repr(self.value)

class VkSession(object):
    def __init__(self,login,password):
        self.login = login
        self.password = password
        self.hashes = {}
        self.auth()
        
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
        form = page.forms[0]
        form.fields['email'] = self.login
        form.fields['pass'] = self.password
        response = self.session.post(form.action, data=form.form_values())
        if "onLoginDone" not in response.text: raise invalid_password("invalid password!")
        return

    def method(self,method,v='5.130',**params):
        if method not in self.hashes:
            self._get_hash(method)
        data = {'act': 'a_run_method','al': 1,
                'hash': self.hashes[method],
                'method': method,
                'param_v':v}
        for i in params:
            data["param_"+i] = params[i]
        answer = self.post_act('https://vk.com/dev', 'a_run_method', data)
        return json.loads(answer[0])['response']
    
    def _get_hash(self,method):
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
        self.hashes[method] = hash_0[0]

    def post_act(self, url, act, data):
        data['al'] = 1
        data['act'] = act
        res = self.session.post(url, data=data)
        if res:
            result = res.text.replace("<!--", "")
            result = json.loads(result)['payload'][-1]
            return result
