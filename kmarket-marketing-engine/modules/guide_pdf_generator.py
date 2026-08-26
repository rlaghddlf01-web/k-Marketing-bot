import logging
from pathlib import Path
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config import OUTPUTS_DIR
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker

logger = logging.getLogger("GuidePDFGenerator")

class GuidePDFGenerator:
    """
    [무인 자동화] 유학생 & 체류 외국인 리드 마그넷 PDF 가이드북 렌더러
    - K-Market 전용: 로컬 라이프 & 0원 나눔 가이드북
    - EasyTax 전용: 조특법 외국인 세무 환급 가이드북 (공인 면책 포함)
    """
    def __init__(self, db_mgr: DBManager):
        self.db_mgr = db_mgr
        self.output_dir = OUTPUTS_DIR / "pdf_guides"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_kmarket_guide(self, filename: str = "kmarket_expat_life_guide.pdf") -> Path:
        """🛒 K-Market 전용 로컬 라이프 & 0원 나눔 가이드북 PDF 생성"""
        file_path = self.output_dir / filename
        c = canvas.Canvas(str(file_path), pagesize=letter)
        
        # 커버
        c.setFont("Helvetica-Bold", 22)
        c.drawString(60, 720, "2026 K-Market Expat Life & Moving Guide")
        c.setFont("Helvetica", 13)
        c.drawString(60, 690, "How to get 0 KRW Free Furniture & Avoid Secondhand Scams in Korea")
        c.line(60, 670, 550, 670)

        # 1. 0원 나눔 & 무빙세일
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, 630, "1. Grabbing 0 KRW Free Furniture & Moving Sales")
        c.setFont("Helvetica", 11)
        c.drawString(70, 605, "- Graduating students leave desks, beds, and fridges for 0 KRW in Feb & Aug.")
        c.drawString(70, 585, "- Over 270 verified items listed daily across 30 university campuses.")
        c.drawString(70, 565, "- Claim free items directly: https://k-market.app")

        # 2. 17개국 양방향 번역 채팅
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, 520, "2. Direct Chat with Zero Language Barrier")
        c.setFont("Helvetica", 11)
        c.drawString(70, 495, "- Built-in real-time 17-language instant translation enabled.")
        c.drawString(70, 475, "- Chat in your native tongue (Vietnamese, Russian, Chinese, Uzbek, etc).")

        # 3. 사기 예방 수칙
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, 430, "3. Safe Expat Direct Deals Checklist")
        c.setFont("Helvetica", 11)
        c.drawString(70, 405, "- Meet near university subways or dormitory main gates for pickup.")
        c.drawString(70, 385, "- Use verified ARC user authentication.")

        c.setFont("Helvetica-Oblique", 9)
        c.drawString(60, 60, "Published by K-Market Global Growth Engine - Free Expat Community Guide")
        c.showPage()
        c.save()
        logger.info(f"🛒 K-Market PDF 가이드북 렌더링 완료: {file_path.name}")
        return file_path

    def generate_easytax_guide(self, filename: str = "easytax_tax_refund_guide.pdf") -> Path:
        """💰 EasyTax 전용 조특법 외국인 세무 환급 가이드북 PDF 생성"""
        file_path = self.output_dir / filename
        c = canvas.Canvas(str(file_path), pagesize=letter)
        
        # 커버
        c.setFont("Helvetica-Bold", 22)
        c.drawString(60, 720, "2026 EasyTax Expat Tax Relief & Refund Guide")
        c.setFont("Helvetica", 13)
        c.drawString(60, 690, "Article 30 Income Tax Reduction & 5-Year Retroactive Refund Manual")
        c.line(60, 670, 550, 670)

        # 1. 조특법 90% 소득세 감면
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, 630, "1. E-9/H-2 Workers: Up to 90% Income Tax Reduction")
        c.setFont("Helvetica", 11)
        c.drawString(70, 605, "- Restriction of Special Taxation Act (Article 30) for SME workers.")
        c.drawString(70, 585, "- Valid for young workers (ages 15-34, extended for military service).")
        c.drawString(70, 565, "- Official calculation: https://easytax.app")

        # 2. D-2 유학생 3.3% 원천징수 환급
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, 520, "2. D-2 Students: 100% Refund on 3.3% Part-Time Tax")
        c.setFont("Helvetica", 11)
        c.drawString(70, 495, "- Freelance/Part-time 3.3% withholding tax is fully refundable if income is under basic threshold.")
        c.drawString(70, 475, "- 5-year retroactive claim available (2020~2025).")

        # 3. Anti-Ban 및 국세청 공인 대리
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, 430, "3. 100% Free AI Simulation & Zero Upfront Fees")
        c.setFont("Helvetica", 11)
        c.drawString(70, 405, "- No advance payments required. 3-minute instant free check.")
        c.drawString(70, 385, "- Processed legally via certified tax accountants registered with National Tax Service.")

        c.setFont("Helvetica-Oblique", 9)
        c.drawString(60, 60, "Published by EasyTax (KTRS) - Certified Expat Tax Advisory Network")
        c.showPage()
        c.save()
        logger.info(f"💰 EasyTax PDF 가이드북 렌더링 완료: {file_path.name}")
        return file_path
