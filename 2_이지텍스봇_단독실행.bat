@echo off
chcp 65001 > nul
title 💰 EasyTax 국세청 외국인 세금환급 전담 봇
cd /d "%~dp0kmarket-marketing-engine"

echo ========================================================
echo 💰 [EasyTax] 100%% 전담 무인 세금환급 봇을 시작합니다.
echo ========================================================
python run_easytax.py
pause
