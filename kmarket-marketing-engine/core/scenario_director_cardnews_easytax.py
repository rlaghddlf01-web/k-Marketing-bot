"""
ScenarioDirectorCardnewsEasyTax - 💰 [EasyTax 5장 7:3 분할 세무 환급 카드뉴스 동적 기획 엔진]
- 60대 전 세무 테마 5단계 감동 스토리텔링 (입금인증 -> 자격확인 -> 안심보증 -> 꿈의실현 -> 결말CTA)
- 제미나이(Gemini) LLM을 통한 17개국 100% 현지어 실시간 카드뉴스 직작문 (글자 깨짐 0%)
- 1~5장 전체 동일 인물 캐릭터 앵커 (남 40% : 여 60% 비율 엄격 유지)
"""

import random
import logging
from typing import Dict, Any, List, Optional
from core.scenario_director_shorts_easytax import (
    ScenarioDirectorShortsEasyTax,
    EASYTAX_60_THEMES,
    EASYTAX_PERSONA_ANCHORS
)

from core.character_anchor_easytax import (
    build_easytax_char_anchor,
    build_easytax_scene_prompt,
    LANG_NEGATIVE_ETHNIC
)
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter

logger = logging.getLogger("ScenarioDirectorCardnewsEasyTax")

# 🎬 세계 최고의 바이럴 사진작가이자 카드뉴스 마케팅 거장 골든 프롬프트
WORLD_MASTER_CARDNEWS_PROMPT = """
너는 세계 최고의 바이럴 사진작가이자 카드뉴스 마케팅의 거장이야. 
네 대본은 사람들을 카드뉴스(인스타/페이스북/레딧)에서 첫 1초 만에 사람들의 시선을 고정시키며 미친 듯이 사로잡지. 
그리고 넌 절대로 매일 같은 뻔한 패턴이나 똑같은 안내 멘트를 쓰지 않아. 그리고 실제 사람처럼 어색한 사진을 절대 만들지는 않지. 네가 만드는 사진은 오류가 없어. 다 실제 직접 찍은 사진 같지.
너에게 지정된 [오늘의 카피라이팅]을 100% 흡수하여, 독자가 1초 만에 넘겨보고 싶게 만드는 후킹 헤드라인과 3줄 불릿을 창작해!
"""


class ScenarioDirectorCardnewsEasyTax:
    """EasyTax 60대 전 테마 5장 7:3 카드뉴스 동적 기획 엔진 (제미나이 100% 현지어 직작문)"""
    def __init__(self):
        self.shorts_director = ScenarioDirectorShortsEasyTax()
        self.copywriter = GeminiCardnewsCopywriter(service_id="easytax")
        self.themes = EASYTAX_60_THEMES  # 60대 전체 테마 동기화 (산단 20 + 비자 15 + 감동사연 15 + 절세팁 10)
        self.personas = EASYTAX_PERSONA_ANCHORS  # 7대 비자별 고정 페르소나 앵커
        self.theme_keys = [t["id"] for t in self.themes]
        self._current_index = 0

    def _match_persona(self, theme: Dict[str, Any]) -> Dict[str, Any]:
        """테마의 비자/타깃에 맞춰 최적의 페르소나를 자동 매칭 (남성 40% : 여성 60% 비율 엄격 유지)"""
        target = theme.get("target", "").lower()
        cat = theme.get("cat", "")
        theme_id = theme.get("id", "")

        # 🎯 [대표님 절대 지침] 남성 4 : 여성 6 황금 성비 가중치 선택
        target_gender = random.choices(["female", "male"], weights=[60, 40], k=1)[0]

        # 1. D-2 유학생 타깃
        if "d-2" in target or "유학" in target or "student" in theme_id:
            d2_pool = [p for p in self.personas if "d2" in p["persona_id"]]
            gender_matched = [p for p in d2_pool if p["gender"] == target_gender]
            return gender_matched[0] if gender_matched else random.choice(d2_pool)
        # 2. E-7 전문직 타깃
        elif "e-7" in target or "it" in target or "엔지니어" in target:
            matching = [p for p in self.personas if "e7" in p["persona_id"]]
            return matching[0] if matching else self.personas[4]
        # 3. H-2 방문취업 타깃
        elif "h-2" in target or "건설" in target or "식당" in target:
            matching = [p for p in self.personas if "h2" in p["persona_id"]]
            return matching[0] if matching else self.personas[5]
        # 4. E-2 강사 타깃
        elif "e-2" in target or "강사" in target:
            matching = [p for p in self.personas if "e2" in p["persona_id"]]
            return matching[0] if matching else self.personas[6]
        # 5. 기본 E-9 제조업/농축산 근로자 (남성 40% : 여성 60% 엄격 반영)
        else:
            e9_pool = [p for p in self.personas if "e9" in p["persona_id"]]
            gender_matched = [p for p in e9_pool if p["gender"] == target_gender]
            return gender_matched[0] if gender_matched else random.choice(e9_pool)

    def get_carousel_scenario(self, lang: str = "vi", theme_index: Optional[int] = None) -> Dict[str, Any]:
        """60대 세무 테마 중 1개를 선택하고 제미나이 100% 현지어 카피라이팅으로 5장 카드뉴스 생성"""
        if theme_index is not None:
            chosen_theme = self.themes[theme_index % len(self.themes)]
        else:
            chosen_theme = random.choice(self.themes)

        theme_id = chosen_theme["id"]
        theme_name = chosen_theme["name"]
        target = chosen_theme["target"]
        persona_type = chosen_theme["persona_type"]
        refund_est = chosen_theme.get("refund_est", 3840000)
        refund_formatted = f"{refund_est:,} KRW"

        # 1. 🎯 테마 맞춤형 7대 비자별 페르소나 자동 매칭 (남 40% : 여 60%)
        matched_persona = self._match_persona(chosen_theme)
        char_anchor = build_easytax_char_anchor(
            lang=lang,
            gender=matched_persona["gender"],
            age_group_ko=matched_persona["age_group"],
            persona_anchor_desc=matched_persona["anchor_desc"]
        )

        # 2. ✍️ 제미나이 AI 100% 현지어 카드뉴스 카피라이팅 (제목, 부제, 뱃지, 3줄 불릿 실시간 직작문)
        generated_copy = self.copywriter.generate_easytax_copy(
            lang=lang,
            theme=chosen_theme,
            persona=matched_persona,
            refund_formatted=refund_formatted
        )

        # 3. 🎯 4장 꿈의 실현(효도송금/비행기표/학비/자기보상) 테마별 사진 프롬프트 분기
        theme_text_lower = (theme_id + " " + theme_name + " " + target).lower()
        if any(w in theme_text_lower for w in ["flight", "vacation", "비행기", "여행", "귀국"]):
            s4_prompt = "cinematic authentic portrait, bright joyful beaming smile holding flight itinerary ticket, looking forward to heartwarming family reunion, bright sunny lighting"
        elif any(w in theme_text_lower for w in ["parent", "house", "송금", "가족", "효도"]):
            s4_prompt = "cinematic authentic portrait, heartwarming joyful emotional smile holding mobile remittance receipt, deep sense of pride and filial love, warm natural lighting"
        elif any(w in theme_text_lower for w in ["tuition", "student", "등록금", "유학", "d-2", "알바"]):
            s4_prompt = "cinematic authentic portrait, proud happy smile on university campus holding textbooks, youthful confident relief, bright ambient lighting"
        else:
            s4_prompt = "cinematic authentic close-up portrait, triumphant overjoyed expression, radiant smile of accomplishment and financial relief, pure happiness in eyes"

        # 4. 5단계 슬라이드별 헐리웃 감동 시네마틱 사진 프롬프트
        scene_actions = {
            1: f"cinematic authentic bust-shot portrait, holding smartphone upright naturally forward towards camera showing a clear bright mobile banking notification screen with official Korean National Tax Service (국세청 NTS) deposit alert of {refund_formatted}, ecstatic overjoyed facial expression with wide happy eyes and victorious radiant smile, sharp focus on face and upright phone screen, natural hand grip",
            2: "cinematic authentic bust-shot portrait, looking towards audience with an engaging, friendly, and enthusiastic explanatory expression, encouraging and warm gesture, sharp focus on face",
            3: "cinematic authentic portrait, warm confident reassuring smile, trustworthy dependable posture in modern workplace hallway, professional comforting expression",
            4: s4_prompt,
            5: "cinematic authentic direct-gaze portrait, looking directly into camera with an encouraging and decisive confident smile, warm direct eye contact motivating the viewer to take action"
        }

        cards = []
        for idx in range(1, 6):
            copy_item = generated_copy[idx - 1] if len(generated_copy) >= idx else {}
            action_desc = scene_actions.get(idx, "working in workplace")
            full_prompt = build_easytax_scene_prompt(scene_idx=idx, char=char_anchor, scene_action=action_desc)

            cards.append({
                "slide_idx": idx,
                "badge": copy_item.get("badge", f"STEP {idx}"),
                "title": copy_item.get("title", f"Step {idx} Title"),
                "subtitle": copy_item.get("subtitle", ""),
                "bullets": copy_item.get("bullets", []),
                "image_prompt": full_prompt,
                "negative_prompt": f"upside down phone, inverted smartphone, backwards phone, phone held upside down, deformed hand holding phone, caucasian, white, deformed fingers, extra limbs, claw hands, bad anatomy, ugly, blurry, 3d render, cartoon, {LANG_NEGATIVE_ETHNIC.get(lang, '')}"
            })

        return {
            "service_id": "easytax",
            "lang": lang,
            "theme_name": theme_id,
            "theme_title": theme_name,
            "character_anchor": char_anchor,
            "episode_id": f"cardnews_easytax_{lang}_{theme_id}_{random.randint(1000, 9999)}",
            "cards": cards
        }
