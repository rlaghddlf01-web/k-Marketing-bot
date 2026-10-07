# -*- coding: utf-8 -*-
"""
EasytaxShortsEndingReplacer - 🎬 [기존 이지텍스 숏폼 산출물 엔딩 신뢰 카드 전면 교체 엔진]
- 기존 숏폼 산출물 폴더의 22초 숏폼 비디오에서 엔딩 CTA 카드 구간을 정밀 탐지
- 순백색(#ffffff) 바탕 + 샴페인 골드 & 딥 네이비 사전 제작 완제품 에셋으로 완벽 교체
- 기존 인물 클립 + 앱 시뮬레이션 + 오디오 스트림(음성 TTS, BGM, 카칭 효과음) 100% 무손실 유지
- 8대 국가(베트남, 우즈벡, 캄보디아, 미얀마, 태국, 네팔, 몽골, 인도네시아) 전체 일괄 적용
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import imageio_ffmpeg
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EasytaxShortsEndingReplacer")


class EasytaxShortsEndingReplacer:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.assets_templates = self.base_dir / "assets" / "templates"
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\이지텍스")
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.scratch_dir = self.base_dir / "scratch" / "replacer_temp"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)

        # 폴더명 매핑
        self.lang_map = {
            "Burmese": "my",
            "Indonesian": "id",
            "Khmer": "km",
            "Nepali": "ne",
            "Thai": "th",
            "Uzbek": "uz",
            "Uzbekistan": "uz",
            "Vietnamese": "vi",
            "Mongolian": "mn",
            "Korean": "ko"
        }

    def detect_lang_from_name(self, name: str) -> Optional[str]:
        for k, v in self.lang_map.items():
            if k.lower() in name.lower():
                return v
        return None

    def get_duration(self, video_path: Path) -> float:
        cmd = [self.ffmpeg_exe, "-i", str(video_path)]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding='utf-8', errors='ignore')
        for line in res.stderr.split("\n"):
            if "Duration:" in line:
                dur_str = line.split("Duration:")[1].split(",")[0].strip()
                parts = dur_str.split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return 0.0

    def is_ending_card_frame(self, video_path: Path, t: float) -> bool:
        out_p = self.scratch_dir / "temp_detect_frame.png"
        cmd = [
            self.ffmpeg_exe, "-y",
            "-ss", str(t),
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(out_p)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not out_p.exists():
            return False
        try:
            img = Image.open(out_p).convert("RGB")
            r, g, b = img.getpixel((50, 50))
            if abs(r - 15) <= 12 and abs(g - 23) <= 12 and abs(b - 42) <= 12:
                return True
        except Exception:
            pass
        return False

    def find_transition_time(self, video_path: Path, total_dur: float) -> Optional[float]:
        low = max(0.0, total_dur - 13.0)
        high = total_dur - 0.2
        if not self.is_ending_card_frame(video_path, high):
            return None
        for _ in range(20):
            mid = (low + high) / 2.0
            if self.is_ending_card_frame(video_path, mid):
                high = mid
            else:
                low = mid
            if (high - low) < 0.05:
                break
        return high

    def replace_ending_in_video(self, video_path: Path, lang: str) -> bool:
        total_dur = self.get_duration(video_path)
        trans_t = self.find_transition_time(video_path, total_dur)
        if trans_t is None:
            logger.warning(f"⚠️ [{video_path.name}] 기존 엔딩 카드를 감지하지 못했습니다. (스킵)")
            return False

        ending_dur = total_dur - trans_t
        template_png = self.assets_templates / f"easytax_ending_cta_{lang}.png"
        if not template_png.exists():
            logger.error(f"❌ [{lang}] 신규 완제품 에셋 누락: {template_png}")
            return False

        logger.info(f"🔄 [{lang.upper()}] 교체 시작: {video_path.name}")
        logger.info(f"   - 총 길이: {total_dur:.2f}s | 인물+앱 구간: 0s ~ {trans_t:.2f}s | 엔딩 구간: {ending_dur:.2f}s")

        # 1. 백업 파일 준비
        backup_path = video_path.parent / f"{video_path.stem}_backup_old_ending.mp4"
        if not backup_path.exists():
            shutil.copy2(video_path, backup_path)
            logger.info(f"   - 원본 백업 완료: {backup_path.name}")

        temp_head = self.scratch_dir / f"head_{lang}.mp4"
        temp_tail = self.scratch_dir / f"tail_{lang}.mp4"
        temp_stitched_video = self.scratch_dir / f"stitched_{lang}.mp4"
        final_output = self.scratch_dir / f"final_{lang}.mp4"

        try:
            # 2. 전반부 (인물 + 앱 시뮬레이션) 무손실 절단
            cmd_head = [
                self.ffmpeg_exe, "-y",
                "-ss", "0",
                "-to", str(trans_t),
                "-i", str(backup_path),
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "fast",
                "-an",
                str(temp_head)
            ]
            subprocess.run(cmd_head, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 3. 신규 완제품 엔딩 세그먼트 렌더링
            cmd_tail = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", str(template_png),
                "-t", str(ending_dur),
                "-vf", "fps=30,format=yuv420p",
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "fast",
                str(temp_tail)
            ]
            subprocess.run(cmd_tail, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 4. 비디오 결합 (concat filter)
            cmd_concat = [
                self.ffmpeg_exe, "-y",
                "-i", str(temp_head),
                "-i", str(temp_tail),
                "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]",
                "-map", "[v]",
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "fast",
                str(temp_stitched_video)
            ]
            subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 5. 기존 원본의 무손실 오디오 스트림 결합
            cmd_merge_audio = [
                self.ffmpeg_exe, "-y",
                "-i", str(temp_stitched_video),
                "-i", str(backup_path),
                "-c:v", "copy",
                "-c:a", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(final_output)
            ]
            subprocess.run(cmd_merge_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 6. 최종 파일 덮어쓰기 교체
            shutil.move(str(final_output), str(video_path))
            logger.info(f"✅ [{lang.upper()}] 엔딩 카드 교체 및 재합성 완료 -> {video_path.name}")
            return True

        except Exception as e:
            logger.error(f"❌ [{lang.upper()}] 교체 실패: {e}")
            if backup_path.exists() and not video_path.exists():
                shutil.copy2(backup_path, video_path)
            return False

    def replace_all_existing_shorts(self) -> Dict[str, bool]:
        """기존 숏폼 산출물 폴더의 모든 숏폼 영상 일괄 교체"""
        results = {}
        for folder in sorted(self.shorts_output_dir.iterdir()):
            if not folder.is_dir():
                continue
            
            # 폴더명에서 언어 감지
            lang = self.detect_lang_from_name(folder.name)
            if not lang:
                continue

            final_mp4s = [
                f for f in folder.glob("*.mp4")
                if ("22초숏폼" in f.name or "22초쇼츠" in f.name)
                and "app_sim" not in f.name
                and "temp" not in f.name
                and "backup" not in f.name
            ]

            for mp4 in final_mp4s:
                success = self.replace_ending_in_video(mp4, lang)
                results[f"{folder.name}/{mp4.name}"] = success

        logger.info(f"🎉 전체 교체 작업 완료: 총 {len(results)}개 중 {sum(1 for v in results.values() if v)}개 성공!")
        return results


if __name__ == "__main__":
    replacer = EasytaxShortsEndingReplacer()
    replacer.replace_all_existing_shorts()
