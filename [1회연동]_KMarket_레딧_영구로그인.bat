@echo off
chcp 65001 > nul
title K-Market Reddit Login
cd /d "%~dp0"
"C:\Users\zkfnt\Python311\python.exe" -u login_kmarket_session.py
pause
