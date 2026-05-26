@echo off
cd /d %~dp0
set HF_ENDPOINT=https://hf-mirror.com
start "口播音频生成 Studio" /min cmd /k python app.py
timeout /t 4 /nobreak >nul
start http://localhost:7860
exit
