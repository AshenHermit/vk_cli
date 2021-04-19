import datetime

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