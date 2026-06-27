@echo off
title Hotel Python Palace

cd /d "%~dp0.."

:menu
cls
echo ================================
echo      HOTEL PYTHON PALACE
echo ================================
echo.
echo 1 - Iniciar website
echo 2 - Iniciar PMS SaaS
echo 3 - Sair
echo.
set /p opcao=Escolha uma opcao: 

if "%opcao%"=="1" goto flask
if "%opcao%"=="2" goto flask_java
if "%opcao%"=="3" exit

echo.
echo Opcao invalida!
pause
goto menu


:flask
cls
echo ================================
echo   A iniciar website
echo ================================
echo.

call venv\Scripts\activate
python app.py

pause
goto menu


:flask_java
cls
echo ================================
echo   A iniciar PMS SaaS
echo ================================
echo.

echo A iniciar PMS SaaS numa nova janela...
start "Hotel Python Palace - PMS SaaS" cmd /k "cd /d "%cd%" && call venv\Scripts\activate && python app.py"

echo.
echo A compilar Dashboard Java...
javac -cp ".;lib\sqlite-jdbc.jar" *.java

if %errorlevel% neq 0 (
    echo.
    echo ERRO NA COMPILACAO!
    pause
    goto menu
)

echo.
echo A iniciar Dashboard Java...
java -cp ".;lib\sqlite-jdbc.jar" HotelPythonPalaceDashboard

pause
goto menu