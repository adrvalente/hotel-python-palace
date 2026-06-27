@echo off
title Hotel Python Palace Dashboard

REM Vai para a pasta principal do projeto
cd /d "%~dp0.."

echo ================================
echo   HOTEL PYTHON PALACE
echo ================================
echo.

echo A compilar...
javac -cp ".;lib\sqlite-jdbc.jar" *.java

if %errorlevel% neq 0 (
    echo.
    echo ERRO NA COMPILACAO!
    pause
    exit
)

echo.
echo A iniciar aplicacao...
java -cp ".;lib\sqlite-jdbc.jar" HotelPythonPalaceDashboard

pause