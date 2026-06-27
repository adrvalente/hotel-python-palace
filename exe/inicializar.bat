@echo off

REM Vai para a pasta acima da pasta exe
cd /d "%~dp0.."

REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Executa o app.py
python app.py

pause