@echo off
set PREV_WD=%cd%
cd /D "%~dp0../"
python "vk_cli.py" %*
cd /D "%PREV_WD%"