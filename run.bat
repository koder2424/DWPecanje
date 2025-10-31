@echo off
REM Prebaci u folder gde se .bat nalazi
pushd "%~dp0"

REM Aktiviraj venv (pozovi .bat verziju)
call "venv\Scripts\activate.bat"

REM Pokreni skriptu
py "main.py"

REM Vrati se nazad u prethodni folder
popd
exit /b
