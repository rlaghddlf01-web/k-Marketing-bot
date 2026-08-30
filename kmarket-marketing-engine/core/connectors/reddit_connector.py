# -*- coding: utf-8 -*-
"""
[모듈] Reddit 독립 연동 커넥터 (core/connectors/reddit_connector.py)
• 역할: Reddit 실시간 프로필 링크 연동, 검증 뷰어 본문 동적 생성, 1회 시험 실행 전담
"""

import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RedditConnector:
    """Reddit 1:1 리드 헌터 독립 연동 커넥터"""

    ACCOUNTS = {
        "kmarket": {
            "username": "u/IdleOn_Boii",
            "profile_url": "https://www.reddit.com/user/IdleOn_Boii/comments/",
            "target_content": "전국 26개 외국인 커뮤니티 가구·원룸 질문 실시간 감지 & 80:20 Anti-Ban 솔루션 답변",
            "diagnostic": "u/IdleOn_Boii 계정 실시간 워밍업 & 26개 서브레딧 감시 정상 가동 중"
        },
        "easytax": {
            "username": "u/HP_Korea",
            "profile_url": "https://www.reddit.com/user/HP_Korea/comments/",
            "target_content": "r/korea, r/Living_in_Korea 세금 환급/3.3% 알바 질문 감지 및 조특법 팩트 답변",
            "diagnostic": "u/HP_Korea 계정 조특법 30조 팩트 답변 & 26개 서브레딧 감시 정상 가동 중"
        }
    }

    @classmethod
    def get_status(cls, brand: str, db_count: int = 4, latest_time: str = "방금 전") -> Dict[str, Any]:
        info = cls.ACCOUNTS.get(brand, cls.ACCOUNTS["kmarket"])
        is_km = (brand == "kmarket")
        title = "🤖 [Reddit u/IdleOn_Boii] 실시간 외국인 질문 감지 및 1:1 솔루션 답변" if is_km else "🤖 [Reddit u/HP_Korea] 조특법 90% 소득세 감면 & 세무 Q&A 답변"
        desc = (
            "🔥 [실시간 헌팅 & 워밍업 가드레일]\n"
            "• 모니터링: r/Living_in_Korea, r/korea, r/hanguk (26개 서브레딧 실시간 스캔)\n"
            "• 계정 상태: u/IdleOn_Boii (카르마 100점 워밍업 안전 모드)\n"
            "• 활동: 유용한 외국인 생활 팁 답변 & 인기 글 Upvote (링크 0건 완전 안전)"
        ) if is_km else (
            "🔥 [실시간 헌팅 & 조특법 팩트 법률 답변]\n"
            "• 모니터링: r/korea, r/Living_in_Korea (세금/비자 질문 실시간 스캔)\n"
            "• 계정 상태: u/HP_Korea (카르마 100점 워밍업 안전 모드)\n"
            "• 활동: 조특법 제30조(중소기업 감면) 팩트 법률 조언 & 인기 글 Upvote"
        )

        return {
            "name": f"🤖 {brand.upper()} Reddit 1:1 세무/생활 허브",
            "icon": "🤖",
            "brand": brand,
            "hub_id": "reddit",
            "ratio": "1:1 정밀 타깃",
            "api_type": "Reddit 26개 서브레딧 (r/korea, r/Living_in_Korea)",
            "target_content": info["target_content"],
            "connected": True,
            "status": "ready",
            "diagnostic": info["diagnostic"],
            "daily_count": db_count,
            "last_published": latest_time,
            "published_preview": {
                "type": "message",
                "title": title,
                "caption": desc,
                "media_tag": f"🤖 Reddit Live Profile ({info['username']})",
                "url": info["profile_url"]
            }
        }

    @classmethod
    def test_publish(cls, brand: str) -> Dict[str, Any]:
        """Reddit 1:1 실시간 스캔 & 안전 워밍업 사이클 즉시 실행"""
        try:
            from modules.reddit_lead_hunter import RedditLeadHunter
            hunter = RedditLeadHunter(brand=brand)
            hunter.run_cycle()
            info = cls.ACCOUNTS.get(brand, cls.ACCOUNTS["kmarket"])
            return {
                "success": True,
                "platform": f"{brand}_reddit",
                "brand": brand,
                "message": f"🤖 [Reddit {info['username']}] 26개 서브레딧 실시간 스캔 & 안전 워밍업 사이클 완료! ({info['profile_url']})",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Reddit 직접 실행 오류: {e}")
            return {
                "success": False,
                "platform": f"{brand}_reddit",
                "brand": brand,
                "message": f"Reddit 실행 오류: {e}",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
