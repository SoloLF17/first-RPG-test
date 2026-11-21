@echo off
setlocal
cd /d "%~dp0.."

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller --noconfirm --clean --onedir --name DueloDeVeyrion --add-data "jogo/assets;jogo/assets" jogo\__main__.py
if errorlevel 1 exit /b 1

copy /y LICENSE dist\DueloDeVeyrion\LICENSE >nul
powershell -NoProfile -Command "Compress-Archive -Path 'dist\DueloDeVeyrion' -DestinationPath 'dist\duelo-veyrion-windows-x64.zip' -Force"
echo Arquivo gerado: dist\duelo-veyrion-windows-x64.zip
