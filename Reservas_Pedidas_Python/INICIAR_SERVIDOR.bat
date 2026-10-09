@echo off
chcp 65001 > nul
title Sistema de Reservas - Pedidas de Mano
cd /d "%~dp0"

echo =================================================================
echo   💍 INICIANDO SERVIDOR WEB DE PEDIDAS DE MANO Y NOVIOS
echo =================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run.py
    goto fin
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py run.py
    goto fin
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python3 run.py
    goto fin
)

echo [ERROR] No se encontro Python instalado en el sistema.
echo Por favor asegurate de tener Python 3 instalado y agregado al PATH.
echo.

:fin
echo.
pause
