@echo off
title Clube 3D Brasil — Agendador
color 0A
cls

echo.
echo  ========================================
echo   CLUBE 3D BRASIL — AUTOMACAO DE POSTS
echo  ========================================
echo.
echo  Iniciando agendador em background...
echo  Para encerrar, feche esta janela.
echo.

cd /d "%~dp0"

python agendador.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERRO ao iniciar o agendador.
    echo  Verifique se o Python esta instalado e
    echo  se voce executou: python setup.py
    pause
)
