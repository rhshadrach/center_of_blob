#!/bin/bash

version=$(</home/richard/dev/center_of_blob/center_of_blob/VERSION)
# strip whitespace
version="$(echo $version | xargs)"

echo "Compiling CoB version $version"

wine ~/.wine/drive_c/users/richard/AppData/Local/Programs/Python/Python310/Scripts/pyinstaller.exe \
 --add-data "/home/richard/dev/center_of_blob/center_of_blob/VERSION;center_of_blob" \
 --add-binary "/home/richard/.wine/drive_c/users/richard/AppData/Local/Programs/Python/Python310/Lib/site-packages/Shapely.libs;Shapely.libs" \
 --hidden-import range_slider \
 --onefile center_of_blob/main.py \
 --name "cob_$version.exe"
