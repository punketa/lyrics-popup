@echo off
title Lyrics Popup v1

cd /d "%~dp0"

echo ================================
echo       LYRICS POPUP v1
echo ================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encuentra el entorno virtual.
    echo.
    echo Asegurate de tener la carpeta .venv
    echo en la raiz del proyecto.
    echo.
    pause
    exit /b 1
)

echo Iniciando Lyrics Popup...
echo.

".venv\Scripts\python.exe" main.py

echo.
echo ================================
echo       Lyrics Popup cerrado
echo ================================
pause