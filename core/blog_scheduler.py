"""
BlogScheduler - ⏰ 100% 대한민국 표준시(KST) 기반 하루 3회 정시 자율 발행 스케줄러
- 골든타임 3회 지정: 아침 09:00, 점심 13:00, 저녁 19:00 (KST)
- 무인 가동 시: 최초 1회 즉시 실행 ➔ 다음 골든타임까지 안전 대기
- 하루 중복 발행 방지 및 24시간 자율주행 보장
"""

import time
import logging
import datetime
from typing import Callable, Optional
from config import KST, get_now_kst, get_now_kst_str

logger = logging.getLogger("BlogScheduler")

# 🎯 하루 3대 외국인 골든타임 (한국 시각 KST 기준)
DAILY_GOLDEN_HOURS = [9, 13, 19]  # 09:00, 13:00, 19:00


class BlogScheduler:
    """블로그 전용 하루 3회 정시 자율 발행 스케줄러"""

    def __init__(self, service_id: str, publish_fn: Callable[[], str]):
        self.service_id = service_id
        self.publish_fn = publish_fn
        self.last_published_slot = None  # 예: "2026-08-29_09" (중복 발행 방지)

    def get_next_target_datetime(self) -> datetime.datetime:
        """다음 골든타임(09:00, 13:00, 19:00 KST) datetime 객체 반환"""
        now = get_now_kst()
        current_hour = now.hour
        current_minute = now.minute
        current_second = now.second

        # 오늘의 남은 골든타임 탐색
        target_hour = None
        for h in DAILY_GOLDEN_HOURS:
            if h > current_hour or (h == current_hour and current_minute == 0 and current_second == 0):
                target_hour = h
                target_date = now.date()
                break

        # 오늘 남은 시간이 없으면 내일 첫 골든타임(09:00)
        if target_hour is None:
            target_hour = DAILY_GOLDEN_HOURS[0]
            target_date = now.date() + datetime.timedelta(days=1)

        return datetime.datetime(
            target_date.year, target_date.month, target_date.day,
            target_hour, 0, 0, tzinfo=KST
        )

    def get_seconds_until_next_run(self) -> int:
        """다음 골든타임까지 남은 초(seconds) 계산"""
        now = get_now_kst()
        target_dt = self.get_next_target_datetime()
        diff = (target_dt - now).total_seconds()
        return max(5, int(diff + 1))

    def run_scheduled_loop(self, is_running_checker: Callable[[], bool], on_log: Optional[Callable[[str, str], None]] = None):
        """
        무인 자율 가동 루프:
        1. 최초 시작 시 1회 즉시 실행
        2. 다음 골든타임까지 안전 sleep
        3. 정시에 1회씩만 발행 (하루 딱 3회)
        """
        log = on_log or (lambda msg, lvl="info": logger.info(msg))
        service_tag = "K-Market" if self.service_id == "kmarket" else "EasyTax"
        
        log(f"🚀 [{service_tag} 블로그] 대한민국 표준시(KST) 하루 3회 (09:00 / 13:00 / 19:00) 안심 스케줄러 가동!", "success")

        # 1. 최초 가동 시 1회 즉시 발행
        if is_running_checker():
            try:
                now_kst = get_now_kst()
                slot_key = f"{now_kst.strftime('%Y-%m-%d')}_{now_kst.hour}"
                self.last_published_slot = slot_key
                
                log(f"⚡ [{service_tag} 블로그] 무인 가동 초기 1회 즉시 발행 시작...", "info")
                msg = self.publish_fn()
                log(f"✅ [{service_tag} 블로그 #초기발행] {msg}", "success")
            except Exception as e:
                log(f"❌ [{service_tag} 블로그] 초기 발행 실패: {e}", "error")

        # 2. 다음 골든타임까지 대기하며 하루 3회 정시 실행 루프
        while is_running_checker():
            wait_seconds = self.get_seconds_until_next_run()
            next_time_str = (get_now_kst() + datetime.timedelta(seconds=wait_seconds)).strftime("%m월 %d일 %H:%M")
            log(f"⏳ [{service_tag} 블로그] 다음 자동 발행 시각: {next_time_str} KST (약 {wait_seconds // 60}분 후)", "info")

            # 5초 단위로 쪼개어 대기 (정지 신호 즉각 감지)
            slept = 0
            while slept < wait_seconds and is_running_checker():
                sleep_chunk = min(5, wait_seconds - slept)
                time.sleep(sleep_chunk)
                slept += sleep_chunk

            if not is_running_checker():
                break

            # 정시 실행
            now_kst = get_now_kst()
            slot_key = f"{now_kst.strftime('%Y-%m-%d')}_{now_kst.hour}"
            if self.last_published_slot != slot_key:
                self.last_published_slot = slot_key
                try:
                    log(f"⏰ [{service_tag} 블로그] 골든타임 정시 발행 시작 ({now_kst.strftime('%H:%M')} KST)...", "info")
                    msg = self.publish_fn()
                    log(f"✅ [{service_tag} 블로그 정시발행] {msg}", "success")
                except Exception as e:
                    log(f"❌ [{service_tag} 블로그] 정시 발행 실패: {e}", "error")

        log(f"⏹️ [{service_tag} 블로그] 하루 3회 무인 스케줄러가 정지되었습니다.", "warning")
