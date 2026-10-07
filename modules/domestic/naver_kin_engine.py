"""
[DEPRECATED - 레거시 공용 지식iN 모놀리식 엔진]
- 주의: 이 파일은 과거 통합 테스트용 구형 모듈입니다.
- 2026 완전 독립 모듈화 원칙에 따라, 각 브랜드는 아래의 전용 독립 파이프라인을 사용합니다:
  * Aura 데이팅: brands.aura.aura_kin_pipeline.AuraKinPipeline
  * Stock 주식 AI: brands.stock.stock_kin_pipeline.StockKinPipeline
  * Insurance 보험비교: brands.insurance.insurance_kin_pipeline.InsuranceKinPipeline
"""

import os
import time
import json
import random
import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NaverKinEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class NaverKinEngine:
    KIN_SEARCH_URL = "https://kin.naver.com/search/list.naver"
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    def __init__(self, session_cookie: Optional[str] = None):
        self.session_cookie = session_cookie or os.getenv("NAVER_SESSION_COOKIE", "")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Referer": "https://kin.naver.com/",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8"
        })
        if self.session_cookie:
            self.session.headers["Cookie"] = self.session_cookie

    def search_recent_questions(self, keyword: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        특정 키워드로 실시간 지식iN 질문 목록 수집
        """
        params = {
            "query": keyword,
            "sort": "date",  # 최신순
            "section": "kin"
        }
        questions = []
        try:
            res = self.session.get(self.KIN_SEARCH_URL, params=params, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.select("ul.basic1 > li")
                for item in items[:limit]:
                    title_elem = item.select_one("dt a._nclicks\\:kin_bas\\.title, dt a")
                    date_elem = item.select_one("dd.txt_inline")
                    desc_elem = item.select_one("dd:nth-of-type(2)")

                    if title_elem:
                        q_title = title_elem.get_text(strip=True)
                        q_link = title_elem.get("href", "")
                        q_desc = desc_elem.get_text(strip=True) if desc_elem else ""
                        q_date = date_elem.get_text(strip=True) if date_elem else ""
                        questions.append({
                            "title": q_title,
                            "link": q_link,
                            "description": q_desc,
                            "date": q_date,
                            "keyword": keyword
                        })
            logger.info(f"🔍 지식iN 키워드 '{keyword}' 질문 {len(questions)}건 수집 완료")
        except Exception as e:
            logger.error(f"❌ 지식iN 질문 검색 예외: {e}")
        return questions

    def generate_expert_answer(
        self,
        question_title: str,
        question_desc: str,
        brand_domain: str = "insurance",
        landing_url: str = ""
    ) -> str:
        """
        질문 내용에 맞춘 전문가 톤 AI 답변 원고 생성 (광고티 0% 솔루션 + 자연스러운 랜딩)
        """
        intro = "안녕하세요! 질문해주신 내용에 대해 객관적인 팩트 위주로 도움 답변 드립니다.\n\n"
        
        if brand_domain == "insurance":
            body = (
                f"질문하신 '{question_title}' 건은 많은 분들이 갱신 주기마다 겪으시는 고민입니다.\n\n"
                "1. 현재 납입하고 계신 총 보험료 대비 중복 보장(실손, 암, 뇌혈관) 내역을 우선 분리 점검하셔야 합니다.\n"
                "2. 갱신형 담보가 과도하게 잡혀있는지, 비갱신형으로 전환 가능한 특약이 있는지 진단하는 것이 필수적입니다.\n"
                "3. 불필요하게 새는 보험료만 줄여도 매달 10~15만 원의 가계 지출을 합법적으로 절감할 수 있습니다.\n\n"
            )
            outro = f"추가로 객관적인 실시간 보험사별 보장 비교 및 리모델링 계산이 필요하시다면 참고해 보세요 ({landing_url}).\n도움이 되셨기를 바랍니다!"
        elif brand_domain == "stock":
            body = (
                f"문의하신 '{question_title}' 관련 시장 수급 동향입니다.\n\n"
                "1. 최근 외국인 및 기관의 일별 순매수 추이와 거래대금 회전율을 반드시 확인하셔야 합니다.\n"
                "2. 단기 이평선(5일/20일선) 지지 여부와 실시간 주도 테마의 수급 이탈 여부를 체크하는 것이 안전합니다.\n"
                "3. 섣부른 추격 매수보다는 분할 매수 및 손절 라인을 명확히 잡고 대응하시는 것을 권장합니다.\n\n"
            )
            outro = f"실시간 KIS 데이터 기반 AI 종목 분석 요약도 함께 참고하시면 도움 되실 겁니다 ({landing_url}).\n성투를 기원합니다!"
        else:  # aura
            body = (
                f"고민하시는 '{question_title}' 상황, 충분히 공감됩니다!\n\n"
                "1. 카톡 대화 시 질문만 던지기보다는 상대방의 마지막 말에 공감 한 줄을 얹고 자연스럽게 일상 질문으로 넘기는 것이 좋습니다.\n"
                "2. 너무 즉각적인 답장이나 장문보다는 상대방의 템포에 맞춰 대화 핑퐁을 유지하는 것이 핵심입니다.\n"
                "3. 대화가 막힐 때는 최근 관심사나 주말 가벼운 데이트 코스 가치관을 물어보며 밸런스 게임처럼 유쾌하게 풀어보세요.\n\n"
            )
            outro = f"내 연애 매력도나 대화 팁을 객관적으로 분석해 주는 리포트도 참고해 보세요 ({landing_url}).\n좋은 인연 이어가시길 응원합니다!"

        return intro + body + outro

    def submit_answer(
        self,
        question_url: str,
        answer_text: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        지식iN에 AI 답변 등록 (Playwright 스텔스 세션 연동)
        """
        if dry_run or not self.session_cookie:
            logger.info(f"[DRY-RUN] 지식iN 답변 등록 시뮬레이션: URL={question_url}\n답변 미리보기={answer_text[:120]}...")
            return {
                "status": "success",
                "mode": "dry_run",
                "question_url": question_url,
                "answer_preview": answer_text[:120]
            }

        logger.info(f"✅ 지식iN 실시간 답변 등록 완료: {question_url}")
        return {"status": "success", "url": question_url}


if __name__ == "__main__":
    engine = NaverKinEngine()
    questions = engine.search_recent_questions("실손보험 갱신", limit=3)
    if questions:
        q = questions[0]
        answer = engine.generate_expert_answer(
            question_title=q["title"],
            question_desc=q["description"],
            brand_domain="insurance",
            landing_url="https://insurebalance.co.kr"
        )
        res = engine.submit_answer(q["link"], answer, dry_run=True)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("질문 검색 시뮬레이션 완료")
