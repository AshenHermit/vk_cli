@echo off
set PREV_WD=%cd%
cd /D "%~dp0../"
python -m "vk_cli.run_vk_cli" %*
cd /D "%PREV_WD%"