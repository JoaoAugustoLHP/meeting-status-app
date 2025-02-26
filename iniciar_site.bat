@echo off
cd /d C:\Users\hbhotelaria\Desktop\Pasta Andreza

:: Inicia o Flask
start cmd /k "venv\Scripts\activate && python app.py"

:: Espera 5 segundos para garantir que o Flask já iniciou
timeout /t 5 /nobreak >nul

:: Inicia o Ngrok
start cmd /k "cd /d C:\Users\hbhotelaria\Desktop\ngrok && ngrok http 5000"
