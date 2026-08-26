import os
import asyncio
import logging
from pathlib import Path
from typing import Optional
from config import LANGUAGES, OUTPUTS_DIR

logger = logging.getLogger("TTSEngine")

class TTSEngine:
    """
    Edge-TTS 기반 17개국 네이티브 성우 음성 합성 엔진
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "shorts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_speech_async(self, text: str, lang: str = "ko", filename: str = "voiceover.mp3") -> Optional[Path]:
        """
        주어진 텍스트를 대상 언어의 네이티브 음성으로 합성하여 mp3 파일로 저장
        """
        lang_config = LANGUAGES.get(lang, LANGUAGES["ko"])
        voice = lang_config.get("voice", "ko-KR-SunHiNeural")
        target_path = self.output_dir / filename

        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(target_path))
            logger.info(f"[{lang.upper()}] TTS 생성 완료: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Edge-TTS 생성 실패 ({lang}, {voice}): {e}")
            return None

    def generate_speech(self, text: str, lang: str = "ko", filename: str = "voiceover.mp3") -> Optional[Path]:
        """동기 래퍼 함수"""
        try:
            return asyncio.run(self.generate_speech_async(text, lang, filename))
        except Exception as e:
            logger.error(f"TTS 동기 실행 에러: {e}")
            return None
