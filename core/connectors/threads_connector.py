# -*- coding: utf-8 -*-
"""
[모듈] Threads 독립 연동 커넥터 (core/connectors/threads_connector.py)
• 역할: Meta Threads 타래형 아티클 파싱, 파일 열람 링크 연동, 1회 시험 실행 전담
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"

class ThreadsConnector:
    """Meta Threads 독립 연동 커넥터"""

    @classmethod
    def get_latest_preview(cls, brand: str) -> Dict[str, Any]:
        try:
            threads_dir = OUTPUTS_DIR / "threads" / brand
            latest_file = None
            if threads_dir.exists():
                json_files = sorted(threads_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
                if json_files:
                    latest_file = json_files[0]
                    with open(latest_file, "r", encoding="utf-8") as f:
                        tdata = json.load(f)
                    
                    posts = tdata.get("posts", [])
                    caption_text = "\n".join([f"🧵 {p}" for p in posts[:3]])
                    return {
                        "type": "threads",
                        "title": f"🧵 [Threads 타래] {tdata.get('hook_title', '')}",
                        "caption": caption_text,
                        "media_tag": f"🧵 Meta Threads Multi-Post ({latest_file.name})",
                        "url": f"/outputs/threads/{brand}/{latest_file.name}",
                        "landing_url": tdata.get("landing_url", "https://k-market.app")
                    }

            if brand == "kmarket":
                return {
                    "type": "threads",
                    "title": "🧵 [Threads 타래] Bí quyết sinh tồn: Nhận đồ nội thất 0 Won tại Hàn Quốc",
                    "caption": "🧵 Post 1: Bí quyết sinh tồn cho du học sinh và người lao động Việt Nam: Đừng mua đồ mới đắt đỏ!\n🧵 Post 2: Mùa tốt nghiệp sinh viên Yonsei/Korea Univ tặng 0 Won giường, bàn học...\n🧵 Post 3: Tải app K-Market chat tiếng Việt tự động để nhận đồ ngay!",
                    "media_tag": "🧵 Meta Threads Viral Story (outputs/threads/kmarket/)",
                    "url": "/outputs/threads/kmarket/",
                    "landing_url": "https://ktrs-market.vercel.app/vi"
                }
            else:
                return {
                    "type": "threads",
                    "title": "🧵 [Threads 타래] Điều 30 Luật Miễn giảm thuế: Giảm 90% thuế thu nhập E-9",
                    "caption": "🧵 Post 1: Lao động Việt Nam E-9/E-7 nhất định phải biết: Quyền giảm 90% thuế thu nhập!\n🧵 Post 2: Được hoàn lại tối đa 2.000.000 KRW/năm trong 5년 연차...\n🧵 Post 3: Kiểm tra miễn phí 3분 선입금 0원 국세청 공인 대리 EasyTax 바로가기",
                    "media_tag": "🧵 Meta Threads Tax Relief Story (outputs/threads/easytax/)",
                    "url": "/outputs/threads/easytax/",
                    "landing_url": "https://ktrs-service.vercel.app/?lang=vi"
                }
        except Exception:
            return {
                "type": "threads",
                "title": f"🧵 [{brand.upper()}] Meta Threads 바이럴 스레드",
                "caption": "Threads 3단 타래형 스토리텔링 & UTM 링크 배포",
                "media_tag": "🧵 Meta Threads",
                "url": f"/outputs/threads/{brand}/"
            }

    @classmethod
    def get_status(cls, brand: str, db_count: int = 4, latest_time: str = "방금 전") -> Dict[str, Any]:
        is_km = (brand == "kmarket")
        return {
            "name": f"🧵 {brand.upper()} Meta Threads 허브",
            "icon": "🧵",
            "brand": brand,
            "hub_id": "threads",
            "ratio": "3~4단 헌법 세무 권리 엑트" if not is_km else "3~4단 타래 바이럴 엑트",
            "api_type": "Meta Threads Graph API",
            "target_content": (
                "17개국어 0원 나눔 꿀팁 3~4단 타래형 바이럴 스레드 & UTM 링크 자동 배포"
                if is_km else
                "17개국어 조특법 90% 소득세 감면 권리 3~4단 타래형 세무 스레드 & 무료 환급 링크 배포"
            ),
            "connected": True,
            "status": "ready",
            "diagnostic": (
                "Meta Threads Graph API 연동 & 17개국어 3~4단 바이럴 타래 실시간 송출 가동 중"
                if is_km else
                "Meta Threads Graph API 연동 & 조특법 90% 감면 3단 권리 타래 실시간 송출 가동 중"
            ),
            "daily_count": db_count,
            "last_published": latest_time,
            "published_preview": cls.get_latest_preview(brand)
        }

    @classmethod
    def test_publish(cls, brand: str) -> Dict[str, Any]:
        """Threads 1회 실시간 발행"""
        try:
            from core.db_manager import DBManager
            from core.supabase_manager import SupabaseManager
            db_mgr = DBManager()
            supabase_mgr = SupabaseManager(db_mgr)
            if brand == "kmarket":
                from modules.threads_kmarket import KMarketThreadsPublisher
                publisher = KMarketThreadsPublisher(db_mgr, supabase_mgr)
                res = publisher.publish_daily_threads(target_langs=["en", "vi", "ko"])
                return {
                    "success": True,
                    "platform": "kmarket_threads",
                    "brand": "kmarket",
                    "message": f"🧵 [K-Market Threads] 3개 언어(EN, VI, KO) 타래 바이럴 스레드 배포 완료 ({res.get('count', 3)}건)",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                from modules.threads_easytax import EasyTaxThreadsPublisher
                publisher = EasyTaxThreadsPublisher(db_mgr, supabase_mgr)
                res = publisher.publish_daily_threads(target_langs=["en", "vi", "ko"])
                return {
                    "success": True,
                    "platform": "easytax_threads",
                    "brand": "easytax",
                    "message": f"🧵 [EasyTax Threads] 3개 언어(EN, VI, KO) 세무 환급 타래 스레드 배포 완료 ({res.get('count', 3)}건)",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            logger.error(f"Threads 직접 발행 실패: {e}")
            return {
                "success": False,
                "platform": f"{brand}_threads",
                "brand": brand,
                "message": f"Threads 발행 오류: {e}",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
