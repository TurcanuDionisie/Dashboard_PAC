#!/bin/sh

echo "creating main executable file "
pyinstaller --onefile --noconfirm main.py

echo "moving main executable file"
mv ./dist/main ./main
rm main.spec

echo "creating directory with files for application"
pyinstaller --onedir --noconfirm dash_app.spec

echo "moving main executable to directory and creating final directory"
mv ./main ./dist/dash_app/
mv ./dist/dash_app/ ./finale_name_of_app_dir

echo "executable creation completed, press enter to continue"
read input