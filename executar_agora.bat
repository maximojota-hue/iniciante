@echo off
title Clube 3D Brasil — Executar Agora
color 0B
cls

echo.
echo  ========================================
echo   CLUBE 3D BRASIL — EXECUCAO MANUAL
echo  ========================================
echo.
echo  Iniciando pipeline agora...
echo.

cd /d "%~dp0"

python agendador.py --agora

echo.
echo  Pipeline concluido. Pressione qualquer tecla para sair.
pause > nul
