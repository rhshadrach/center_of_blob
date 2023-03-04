@echo off

set /p version=<center_of_blob/VERSION
for /F "tokens=* USEBACKQ" %%F in (`where python`) do (
set python_path=%%F
)
SETLOCAL
FOR %%i IN ("%python_path%") DO (
ECHO python_path=%%~pi
)

pyinstaller.exe^
 --add-data "center_of_blob/VERSION;center_of_blob"^
 --add-binary "%python_path%Lib/site-packages/Shapely.libs;Shapely.libs"^
 --hidden-import range_slider^
 --exclude-module _bootlocale^
 --onefile center_of_blob/main.py^
 --name "cob_%version%.exe"
