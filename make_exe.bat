@echo off

set /p version=<cellcensus/VERSION
for /F "tokens=* USEBACKQ" %%F in (`python -c "import site; print(site.getsitepackages()[0])"`) do (
set python_path=%%F
)

pyinstaller.exe^
 --add-data "cellcensus/VERSION;cellcensus"^
 --add-binary "%python_path%\lib\site-packages\Shapely.libs;Shapely.libs"^
 --hidden-import range_slider^
 --exclude-module _bootlocale^
 --onefile cellcensus/main.py^
 --name "CellCensus_%version%.exe"
