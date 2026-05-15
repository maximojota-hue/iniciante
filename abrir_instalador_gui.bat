@echo off
title Clube 3D Brasil - Instalador
cd /d "%~dp0"
python instalador_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Erro ao abrir o instalador. Verifique se o Python esta instalado.
    pause
)
