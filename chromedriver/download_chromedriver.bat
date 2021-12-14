@echo off

set PREV_WD=%cd%
cd /D "%~dp0"

set EXECUTABLE=chromedriver.exe
set ARCHIVE=chromedriver_win32.zip
set VERSION_FILE=version.txt

where /q %EXECUTABLE%
IF errorlevel 1 (
    echo:
    echo add chromedriver location "%~dp0" to PATH
    echo:
) ELSE (
    echo chromedriver is already in path
    exit /b
)

del %EXECUTABLE%
echo:
curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE > %VERSION_FILE%
set /p VERSION= < %VERSION_FILE%
del %VERSION_FILE%
curl https://chromedriver.storage.googleapis.com/%VERSION%/%ARCHIVE% --output %ARCHIVE%
jar -xvf %ARCHIVE%
IF %errorlevel% GEQ 1 (
    echo:
    echo "jar" not working, unpack "%ARCHIVE%" yourself
    echo: 
) else (
    del %ARCHIVE%
)
cd /D "%PREV_WD%"

pause