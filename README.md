# vk cli

A small application for executing Python scripts with access to the VK api at the user level.  
The code has gone through a lot of quick refactors, so it can be difficult to extend, also there is bad error handling, but it is good for small tasks.  
Authorization done with an implicit flow, a browser is used to automate this process, and the browser is chrome.  

## Requirements
* [python 3.9+](https://www.python.org/downloads/)
* [chrome](https://www.google.com/intl/en_us/chrome/) and [chromedriver](https://chromedriver.chromium.org/) (in PATH) - for fast implicit flow authorization

`chromedriver` can be downloaded in *windows* with batch file
```
> chromedriver/download_chromedriver.bat
```

## Installing in Python Scripts
```
> pip install git+https://github.com/AshenHermit/vk_cli.git
or download repo and run
> python setup.py install
```
then launch with:
```
> vk-cli
```

## Installing locally
```
Installing requirements
> pip install -r requirements.txt
```
then launch with:
```
> python vk_cli.py
or
> cmd\vk-cli.bat
```

## Usage session example
<!-- ![screenshot](https://sun9-12.userapi.com/impg/huMKhazegG6RZ-PUKNuK6ceSdKwz_9KshVnUCw/NVn4cpeU6WQ.jpg?size=1635x894&quality=96&sign=129d4ec23d1f40c605b0e377bafbcd3c&type=album) -->
```
vk_cli> _messages

vk_cli _messages> help

characters:
  ";" : separates multiple commands
global commands:
  .. : unselect plugin : ' .. '
  help : show commands and plugins overview : ' help '
  reload : hot reload plugins : ' reload '
  new_plugin : create new plugin : ' new_plugin <plugin name, ex. "cool_tools"> '

plugins list:
  _docs
  _messages
  _users

_messages commands list:
  browse : browse conversations and view messages : 'browse [<count>] [<offset>]'
  chat : [out of order] enter conversation : 'chat <conv index / conv id>'
  send : send message : ' send "<message>" '
  send_raw_attachments : send raw attachments : ' send "<attachments>" '
  get_members_sites : help TODO: get members sites : ' get_members_sites [<conv index / conv id>] '
  compare_names : help TODO: compare names : ' compare_names <names separated with coma> [<conv index / conv id>]'
  show_scrolling_message : sends a message that will be edited and animated as scrolling text : ' show_scrolling_message <message> <title> [<conv index / conv id>]'
  export_attachments : export all conversation attachments into a <directory>/conversation name : ' export_attachments [<types> : empty - all types, not empty - example: "photo video audio doc link"] [<directory>] [<conv index / conv id>]'
  export_messages : export all messages into a json file <filepath> : ' export_messages [<filepath>] [<conv index / conv id>]'

vk_cli _messages> browse 10 10

[0] [ 271557523 ]    Андрей Каблуков
[1] [ --------- ]    ---------
[2] [ --------- ]    ---------
[4] [ --------- ]    ---------
[3] [ 578432022 ]    Moon Moon
[5] [ 2000000031 ]   group bot
[6] [ --------- ]    ---------
[7] [ 344928203 ]    Иван Гусев
[8] [ 100 ]          Администрация ВКонтакте
[9] [ 2000000032 ]   кибир пиздопляски [революции, фотосессии, КоррумпИнвест, локальные memosычи, кеки и маслянство]

vk_cli _messages> chat 344928203

--- Гусев Иван --- 2021-11-14 20:27:54 --
  ЧТОБЫ ВСЕ ПОСЛУШАЛ
------------
--- Гусев Иван --- 2021-11-14 20:29:54 --
  ПРИДУ ПРОВЕРЮ
------------

vk_cli _messages | Иван Гу...> export_attachments

exported files will be located in folder "C:/Users/user/Downloads/vk exports/Иван Гусев"
exporting attachments with media type 'photo'
--- gathering attachments with media type 'photo' from peer '344928203' ...
--- downloading gathered attachments: 100%|█████████████████████████████████████████████████████████████████████████████| 479/479 [00:00<00:00, 634.95it/s, 344928203_457260555]
exporting attachments with media type 'video'
--- gathering attachments with media type 'video' from peer '344928203' ...
--- downloading gathered attachments: 100%|███████████████████████████████████████████████████████████████████████████████| 82/82 [00:00<00:00, 455.44it/s, 344928203_456240551]
exporting attachments with media type 'audio'
--- gathering attachments with media type 'audio' from peer '344928203' ...
--- downloading gathered attachments: 100%|█████████████████████████████████████████████████| 90/90 [00:33<00:00,  2.71it/s, Doren Groff - Сад Сновидений - 576828276_456239108]
exporting attachments with media type 'doc'
--- gathering attachments with media type 'doc' from peer '344928203' ...
--- downloading gathered attachments: 100%|████████████████████████████████████████████████████████████████| 10/10 [00:02<00:00,  3.62it/s, Controller.cs - 344928203_617778115]
exporting attachments with media type 'link'
--- gathering attachments with media type 'link' from peer '344928203' ...
--- downloading gathered attachments: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 14/14 [00:00<00:00, 245.77it/s]

```