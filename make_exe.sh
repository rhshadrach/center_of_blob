#!/bin/bash

version=$(</home/richard/dev/center_of_blob/center_of_blob/VERSION)
# strip whitespace
version="$(echo $version | xargs)"

echo "Compiling CoB version $version"

wine C:/Python38/Scripts/pyinstaller.exe \
 --add-data "/home/richard/dev/center_of_blob/center_of_blob/VERSION;center_of_blob" \
 --hidden-import range_slider \
 --onefile center_of_blob/main.py \
 --name "cob_$version.exe"

# --add-binary "/home/richard/.wine/drive_c/Python38/Lib/site-packages/Shapely.libs;Shapely.libs" \