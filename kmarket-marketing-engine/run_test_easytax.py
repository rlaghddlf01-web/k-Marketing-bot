# -*- coding: utf-8 -*-
import os
import sys
import time
from pathlib import Path

# UTF-8 출력 강제
sys.stdout.reconfigure(encoding='utf-8')

print("🚀 [EasyTax 숏폼 생성기 가동]")
from modules.shorts_easytax import ShortsEasyTax

generator = ShortsEasyTax()
t0 = time.time()
result = generator.produce_shorts(lang="vi", engine_mode="colab_gpu")
elapsed = time.time() - t0

print(f"🎉 [완료] 소요 시간: {elapsed:.1f}초")
print(f"📁 결과 비디오 경로: {result.get('video_path')}")
print(f"📊 씬 수: {len(result.get('scene_images', []))}")
for s in result.get('scene_images', []):
    print(f"  - 씬 {s.get('scene_idx')}: {s.get('image_path') or s.get('video_path')}")
