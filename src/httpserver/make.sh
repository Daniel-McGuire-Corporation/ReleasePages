#!/bin/sh

echo "Installing dependencies"
pip install --user pyinstaller
clear
pip3 install --user pyinstaller
clear

echo "Building Server"
pyinstaller --onefile server.py
clear

echo "Done"