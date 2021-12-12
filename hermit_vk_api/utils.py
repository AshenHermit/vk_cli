import datetime
from pathlib import Path
import re
import subprocess
import os
import urllib

from difflib import SequenceMatcher
def get_string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def string_with_fixed_length(string, length):
    while len(string) < length:
        string += " "
    return string

def html_to_text(html):
    text = html.replace('<br>', '\n')
    return text

def clip_text(text, length, postfix='...'):
    if len(text) + len(postfix) > length:
        text = text[:length - len(postfix)] + postfix
    return text

def get_formated_date(timestampt):
    return datetime.datetime.utcfromtimestamp(timestampt).strftime('%Y-%m-%d %H:%M:%S')

def get_now_formated_date():
    return get_formated_date(datetime.datetime.now().timestamp())

def is_http_url(text):
    if not type(text) is str: return False
    text = text.strip()
    return text[0:4] == "http"

def get_extension_from_url(url):
    ext = ""
    try:
        ext = re.search(r"\.([^\W]+)", url[url.rfind("/"):]).group(1)
    except:
        pass
    return ext


def to_camel_case(text):
    text = text.replace(" ", "_")
    text = "_" + text

    for i in range(4):
        text = text.replace("__", "_")

    word_start_patterns = re.findall(r'_.', text)

    for pat in word_start_patterns:
        text = text.replace(pat, pat[1].upper())

    return text

def open_file_in_editor(filepath):
    folder_path = filepath[:filepath.rfind("/")]
    try:
        os.system(f'code . {filepath}')
        return
    except:
        pass

    os.system(f'explorer {os.path.abspath(folder_path)}')


def encode_uri_component(text):
    text = urllib.parse.quote(text, safe='~()*!.\'')
    return text

def decode_uri_component(text):
    text = urllib.parse.unquote(text)
    return text

def make_dirs(path:Path)->Path:
    if path.as_posix().find(".")!=-1:
        path = (path / "..").resolve()
    os.makedirs(str(path), exist_ok=True)
    return path

def get_existing_path(path:str) -> Path:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        os.makedirs(str(path), exist_ok=True)
    return path

def normalize_filepath_name(filepath:Path):
    filepath = filepath.with_name(re.sub(r'[^\w\-_\. ]', '_', filepath.name))
    return filepath