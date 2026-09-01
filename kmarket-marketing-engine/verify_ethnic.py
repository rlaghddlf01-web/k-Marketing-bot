import sys
sys.stdout.reconfigure(encoding='utf-8')

from core.scenario_director_shorts_easytax import ScenarioDirectorShortsEasyTax
from core.scenario_director_shorts_kmarket import ScenarioDirectorShortsKMarket

print("=== [EasyTax vi - 5씬 이미지 프롬프트 에스닉 앵커 검증] ===")
sd_tax = ScenarioDirectorShortsEasyTax()
plan_tax = sd_tax.plan_daily_scenario(lang='vi')
for s in plan_tax['scenes']:
    prompt = s["image_prompt"][:150]
    has_viet = "Vietnamese" in prompt or "SAME" in prompt
    print(f"Scene {s['scene_idx']}: Vietnamese={has_viet}")
    print(f"  -> {prompt}")
    print()

print("=== [KMarket vi B-mode - 5씬 이미지 프롬프트 에스닉 앵커 검증] ===")
sd_km = ScenarioDirectorShortsKMarket()
plan_km = sd_km.plan_daily_scenario(lang='vi', force_mode='B_gemini_story5')
for s in plan_km['scenes']:
    prompt = s["image_prompt"][:150]
    has_viet = "Vietnamese" in prompt or "SAME" in prompt
    print(f"Scene {s['scene_idx']}: Vietnamese={has_viet}")
    print(f"  -> {prompt}")
    print()
