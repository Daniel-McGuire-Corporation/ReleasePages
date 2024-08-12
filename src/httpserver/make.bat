@echo off

echo Installing Dependencies
pip3 install pyinstaller
cls
pip install pyinstaller
cls

echo Building Server
pyinstaller --onefile startserver.py

echo Done!
exit