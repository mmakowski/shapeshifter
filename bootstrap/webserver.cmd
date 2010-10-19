@echo off
:start
c:\python27\python.exe webserver.py %*
echo exit code: %errorlevel%
if errorlevel 3 goto start
