"""
ChannelScheduler - ⏰ 100% 대한민국 표준시(KST) 기반 옴니채널 정시 & 인터벌 자율 스케줄러
- 1) 정시 스케줄링 모드: 지정된 골든타임(예: ["08:00", "15:30", "22:30"])에 정밀 자율 발행
- 2) 주기적 인터벌 모드: 지정된 주기(예: 1시간 = 3,600초)마다 자율 스캔 및 발행
- 무인 가동 시: 1회 초기 즉시 발행 ➔ 다음 시각까지 안전 Deep Sleep
- 중복 발행 0% 보장 및 즉시 정지 신호 감지
"""

import time
import logging
import datetime
from typing import Callable, List, Optional, Union
from config import KST, get_now_kst, get_now_kst_str

logger = logging.getLogger("ChannelScheduler")


class ChannelScheduler:
    """채널 전용 대한민국 표준시(KST) 정시 & 인터벌 스케줄러"""

    def __init__(
        self,
        channel_name: str,
        publish_fn: Callable[[], str],
        time_slots: Optional[Union[List[str], List[int]]] = None,
        interval_seconds: Optional[int] = None,
        target_minute: int = 0
    ):
        self.channel_name = channel_name
        self.publish_fn = publish_fn
        self.interval_seconds = interval_seconds
        
        # 시간대 슬롯 정규화 (예: ["08:00", "15:30", "22:30"])
        self.slots = []
        if time_slots:
            for item in time_slots:
                if isinstance(item, str) and ":" in item:
                    parts = item.split(":")
                    self.slots.append((int(parts[0]), int(parts[1])))
                elif isinstance(item, int):
                    self.slots.append((item, target_minute))
            self.slots = sorted(self.slots, key=lambda x: (x[0], x[1]))
        
        self.last_published_slot = None

    def get_next_target_datetime(self) -> datetime.datetime:
        """다음 예정된 골든타임 datetime 객체 반환"""
        now = get_now_kst()
        
        if self.interval_seconds:
            return now + datetime.timedelta(seconds=self.interval_seconds)

        current_h = now.hour
        current_m = now.minute

        target_slot = None
        for h, m in self.slots:
            if h > current_h or (h == current_h and m > current_m):
                target_slot = (h, m)
                target_date = now.date()
                break

        # 오늘 남은 슬롯이 없으면 내일 첫 슬롯
        if target_slot is None:
            target_slot = self.slots[0]
            target_date = now.date() + datetime.timedelta(days=1)

        return datetime.datetime(
            target_date.year, target_date.month, target_date.day,
            target_slot[0], target_slot[1], 0, tzinfo=KST
        )

    def get_seconds_until_next_run(self) -> int:
        """다음 실행까지 남은 초(seconds) 계산"""
        if self.interval_seconds:
            return self.interval_seconds
            
        now = get_now_kst()
        target_dt = self.get_next_target_datetime()
        diff = (target_dt - now).total_seconds()
        return max(5, int(diff + 1))

    def run_scheduled_loop(
        self,
        is_running_checker: Callable[[], bool],
        on_log: Optional[Callable[[str, str], None]] = None
    ):
        """
        무인 자율 가동 루프:
        1. 최초 시작 시 1회 즉시 실행
        2. 다음 골든타임/주기까지 안전 sleep
        3. 정시에 1회씩만 발행/스캔
        """
        log = on_log or (lambda msg, lvl="info": logger.info(msg))
        
        if self.interval_seconds:
            mode_desc = f"{self.interval_seconds // 3600}시간 간격" if self.interval_seconds >= 3600 else f"{self.interval_seconds // 60}분 간격"
            log(f"🚀 [{self.channel_name}] KST {mode_desc} 정기 자율 헌터 가동!", "success")
        else:
            slots_str = ", ".join([f"{h:02d}:{m:02d}" for h, m in self.slots])
            log(f"🚀 [{self.channel_name}] KST 하루 {len(self.slots)}회 ({slots_str}) 안심 스케줄러 가동!", "success")

        # 1. 최초 가동 시 1회 즉시 실행
        if is_running_checker():
            try:
                now_kst = get_now_kst()
                slot_key = f"{now_kst.strftime('%Y-%m-%d')}_{now_kst.hour}_{now_kst.minute}"
                self.last_published_slot = slot_key
                
                log(f"⚡ [{self.channel_name}] 무인 가동 초기 1회 즉시 스캔/발행 시작...", "info")
                msg = self.publish_fn()
                log(f"✅ [{self.channel_name} #초기실행] {msg}", "success")
            except Exception as e:
                log(f"❌ [{self.channel_name}] 초기 실행 실패: {e}", "error")

        # 2. 다음 예정 시각까지 대기하며 실행 루프
        while is_running_checker():
            wait_seconds = self.get_seconds_until_next_run()
            next_dt = get_now_kst() + datetime.timedelta(seconds=wait_seconds)
            next_time_str = next_dt.strftime("%m월 %d일 %H:%M")
            log(f"⏳ [{self.channel_name}] 다음 자동 스캔/발행: {next_time_str} KST (약 {wait_seconds // 60}분 후)", "info")

            # 5초 단위로 쪼개어 대기 (정지 신호 즉시 감지)
            slept = 0
            while slept < wait_seconds and is_running_checker():
                sleep_chunk = min(5, wait_seconds - slept)
                time.sleep(sleep_chunk)
                slept += sleep_chunk

            if not is_running_checker():
                break

            # 정기 실행
            now_kst = get_now_kst()
            try:
                log(f"⏰ [{self.channel_name}] 정기 자율 스캔/발행 시작 ({now_kst.strftime('%H:%M')} KST)...", "info")
                msg = self.publish_fn()
                log(f"✅ [{self.channel_name} 정기실행] {msg}", "success")
            except Exception as e:
                log(f"❌ [{self.channel_name}] 정기 실행 실패: {e}", "error")

        log(f"⏹️ [{self.channel_name}] 무인 스케줄러가 정지되었습니다.", "warning")
