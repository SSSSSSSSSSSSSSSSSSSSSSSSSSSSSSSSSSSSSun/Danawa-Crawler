@echo off
setlocal enabledelayedexpansion

REM Clean
del /Q chromedriver-win64

REM Get Chrome version
for /f "tokens=2 delims==" %%a in ('wmic datafile where "name='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'" get Version /value') do set CHROME_VERSION=%%a

REM Determine correct ChromeDriver version
echo Chrome Version: %CHROME_VERSION%

REM Construct download URL
set DOWNLOAD_URL=https://storage.googleapis.com/chrome-for-testing-public/%CHROME_VERSION%/win64/chromedriver-win64.zip
echo DOWNLOAD_URL=%DOWNLOAD_URL%

REM Download ChromeDriver
echo Downloading ChromeDriver...
powershell -Command "Invoke-WebRequest -Uri %DOWNLOAD_URL% -o chromedriver_win64.zip"

REM Unzip ChromeDriver
echo Unzipping ChromeDriver...
powershell -Command "Expand-Archive -Path chromedriver_win64.zip -DestinationPath ."

REM Clean up
del chromedriver_win64.zip
echo Done.