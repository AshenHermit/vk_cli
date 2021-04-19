import datetime
import re
import subprocess
import os

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
