@echo off

set /p version=<center_of_blob/VERSION
for /F "tokens=* USEBACKQ" %%F in (`python -c 'import site; print(site.getsitepackages()[0])'`) do (
set python_path=%%F
)

pyinstaller.exe^
 --add-data "center_of_blob/VERSION;center_of_blob"^
 --add-binary "%python_path%Shapely.libs;Shapely.libs"^
 --hidden-import range_slider^
 --exclude-module _bootlocale^
 --onefile center_of_blob/main.py^
 --name "cob_%version%.exe"
