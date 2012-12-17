@echo off
set PYINSTALLER=C:\pyinstaller
python -O %PYINSTALLER%\pyinstaller.py src/xcat.py -F -o _temp --buildpath=_temp
rm -r -f bin
mkdir bin
mv _temp/dist/xcat.exe bin/xcat.exe
rm -r -f _temp