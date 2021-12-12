@echo off

set EXECUTABLE=chromedriver.exe
set ARCHIVE=chromedriver_win32.zip
set VERSION_FILE=version.txt
del %EXECUTABLE%

where /q "chromedriver.exe"
IF errorlevel 1 (
    echo:
    echo add chromedriver location "%~dp0" to PATH
    echo:
) ELSE (
    echo chromedriver already is in path
)

echo:
curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE > %VERSION_FILE%
set /p VERSION= < %VERSION_FILE%
del %VERSION_FILE%
curl https://chromedriver.storage.googleapis.com/%VERSION%/%ARCHIVE% --output %ARCHIVE%
jar -xvf %ARCHIVE%
del %ARCHIVE%

pause