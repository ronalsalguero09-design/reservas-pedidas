@echo off
chcp 65001 > nul
title Compartir Link Publico para Otras Ciudades y Celulares
cd /d "%~dp0"

echo =================================================================
echo   💍 GENERANDO LINK PUBLICO PARA CUALQUIER CIUDAD Y CELULAR
echo =================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python compartir.py
    goto fin
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py compartir.py
    goto fin
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python3 compartir.py
    goto fin
)

echo [ERROR] No se encontro Python instalado.
echo.
pause

:fin
