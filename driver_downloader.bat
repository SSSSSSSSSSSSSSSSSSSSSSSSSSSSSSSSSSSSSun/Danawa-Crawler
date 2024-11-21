@echo off
setlocal enabledelayedexpansion

REM Download Chrome
Move-Item -Path "C:\hostedtoolcache\windows\setup-chrome\chromedriver\stable\x64\chromedriver.exe" -Destination "$env:GITHUB_WORKSPACE\chromedriver-win64"