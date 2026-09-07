@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title [K-Market] 8개국 골든배치 24시간 무인 데몬

echo ========================================================
echo 🛒 [K-Market] 8대 황금 타깃 국가 24시간 무인 골든배치 데몬
echo ========================================================
echo • 대상 브랜드: K-Market (외국인 커머스 / 무료나눔 / 중고거래)
echo • 타깃 국가: 🇻🇳베트남, 🇺🇿우즈벡, 🇰🇭캄보디아, 🇳🇵네팔, 🇹🇭태국, 🇮🇩인도네시아, 🇲🇳몽골, 🇲🇲미얀마
echo • 골든 슬롯: 매일 오전 11:30 & 저녁 18:30 (하루 2회 자동 대량생산)
echo • 1회 생산: 케이마켓 8개국 숏폼 8편 + 8개국 5장 카드뉴스 8세트
echo • 하루 총합: 숏폼 16편 + 카드뉴스 16세트 (바탕화면 자동 정리)
echo ========================================================
echo.

cd /d "%~dp0kmarket-marketing-engine"
python run_golden_batch.py --brand kmarket --mode daemon

pause
