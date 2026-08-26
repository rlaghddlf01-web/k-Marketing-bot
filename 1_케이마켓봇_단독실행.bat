@echo off
chcp 65001 > nul
title 🛒 K-Market 외국인 0원나눔 전담 무인 봇
cd /d "%~dp0kmarket-marketing-engine"

echo ========================================================
echo 🛒 [K-Market] 100%% 전담 무인 성장봇을 시작합니다.
echo ========================================================
python run_kmarket.py
pause
