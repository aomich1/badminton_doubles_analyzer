@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name BadmintonDoublesAnalyzer --add-data "web;web" app.py
echo.
echo Portable executable: dist\BadmintonDoublesAnalyzer.exe
pause
