"""
ScenarioDirectorCardnewsKMarket - 🛒 [K-Market 5장 7:3 분할 0원 나눔 카드뉴스 동적 기획 엔진]
- 60대 0원 나눔 테마 5단계 감동 스토리텔링 (1:1실물수령 -> 방배치행복 -> 150만절약 -> 17개국앱소개 -> 앱다운CTA)
- 제미나이(Gemini) LLM을 통한 17개국 100% 현지어 실시간 카드뉴스 직작문 (글자 깨짐 0%)
- 1~5장 전체 동일 인물 캐릭터 앵커 (남 40% : 여 60% 비율 엄격 유지)
"""

import random
import logging
from typing import Dict, Any, List, Optional
from core.scenario_director_shorts_kmarket import (
    ScenarioDirectorShortsKMarket,
    KMARKET_60_THEMES,
    KMARKET_PERSONA_ANCHORS
)

from core.character_anchor_cardnews_kmarket import (
    build_kmarket_cardnews_char_anchor,
    build_kmarket_cardnews_scene_prompt,
    build_kmarket_cardnews_negative_prompt,
    LANG_NEGATIVE_ETHNIC
)
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter

logger = logging.getLogger("ScenarioDirectorCardnewsKMarket")

# 🎬 세계 최고의 바이럴 사진작가이자 카드뉴스 마케팅 거장 골든 프롬프트
WORLD_MASTER_CARDNEWS_PROMPT = """
너는 세계 최고의 바이럴 사진작가이자 카드뉴스 마케팅의 거장이야. 
네 대본은 사람들을 카드뉴스(인스타/페이스북/레딧)에서 첫 1초 만에 사람들의 시선을 고정시키며 미친 듯이 사로잡지. 
그리고 넌 절대로 매일 같은 뻔한 패턴이나 똑같은 안내 멘트를 쓰지 않아. 그리고 실제 사람처럼 어색한 사진을 절대 만들지는 않지. 네가 만드는 사진은 오류가 없어. 다 실제 직접 찍은 사진 같지.
너에게 지정된 [오늘의 카피라이팅]을 100% 흡수하여, 독자가 1초 만에 넘겨보고 싶게 만드는 후킹 헤드라인과 3줄 불릿을 창작해!
"""


class ScenarioDirectorCardnewsKMarket:
    """K-Market 60대 전 테마 5장 7:3 카드뉴스 동적 기획 엔진 (제미나이 100% 현지어 직작문)"""
    def __init__(self):
        self.copywriter = GeminiCardnewsCopywriter(service_id="kmarket")
        self.themes = KMARKET_60_THEMES  # 60대 전체 테마 동기화 (대학가 20 + 품목 15 + 자취에피소드 15 + 산단 10)
        self.personas = KMARKET_PERSONA_ANCHORS  # 7대 타깃별 고정 페르소나 앵커
        self.theme_keys = [t["id"] for t in self.themes]
        self._current_index = 0

    def _match_persona(self, theme: Dict[str, Any]) -> Dict[str, Any]:
        """테마의 지역/대상에 맞춰 최적의 페르소나를 자동 매칭 (남성 40% : 여성 60% 비율 엄격 유지)"""
        target = theme.get("target", "").lower()
        cat = theme.get("cat", "")
        theme_id = theme.get("id", "")

        # 🎯 [대표님 절대 지침] 남성 4 : 여성 6 황금 성비 가중치 선택
        target_gender = random.choices(["female", "male"], weights=[60, 40], k=1)[0]

        # 1. 대학가 캠퍼스 타깃 (연세대, 고려대, 성균관대 등)
        if cat == "campus" or "univ" in theme_id or "대학" in target:
            campus_pool = [p for p in self.personas if "d2" in p["persona_id"]]
            gender_matched = [p for p in campus_pool if p["gender"] == target_gender]
            return gender_matched[0] if gender_matched else random.choice(campus_pool)
        # 2. 산업단지 근로자 타깃 (안산, 수원 영통, 평택 등)
        elif cat == "industry" or "ind_" in theme_id or "공단" in target or "산단" in target:
            ind_pool = [p for p in self.personas if "e9" in p["persona_id"]]
            gender_matched = [p for p in ind_pool if p["gender"] == target_gender]
            return gender_matched[0] if gender_matched else random.choice(ind_pool)
        # 3. IT/전문직 타깃 (강남, 구로 등)
        elif "강남" in target or "구로" in target or "디지털" in target:
            it_pool = [p for p in self.personas if "e7" in p["persona_id"] or "f4" in p["persona_id"]]
            gender_matched = [p for p in it_pool if p["gender"] == target_gender]
            return gender_matched[0] if gender_matched else random.choice(it_pool)
        # 4. 일반 품목/자취 에피소드 (남성 40% : 여성 60% 가중치 반영)
        else:
            gender_matched = [p for p in self.personas if p["gender"] == target_gender]
            return random.choice(gender_matched) if gender_matched else random.choice(self.personas)

    def get_carousel_scenario(self, lang: str = "ko", theme_index: Optional[int] = None) -> Dict[str, Any]:
        """카드뉴스 전용 독립 캐릭터 앵커로 1, 2, 5번 슬라이드 100% 동일 인물 보장 5장 카드뉴스 생성"""
        chosen_theme = self.themes[theme_index % len(self.themes)] if theme_index is not None else random.choice(self.themes)
        theme_id = chosen_theme["id"]
        theme_name = chosen_theme["name"]
        target = chosen_theme.get("target", "신촌")
        item = chosen_theme.get("item", "가구")
        cat = chosen_theme.get("cat", "campus")

        # 1. 🎯 테마 맞춤형 페르소나 및 독립 캐릭터 앵커 생성
        matched_persona = self._match_persona(chosen_theme)
        gender = matched_persona.get("gender", "female")
        age_group = matched_persona.get("age_group", "20대 중반")
        anchor_desc = matched_persona.get("anchor_desc", "")

        char_anchor = build_kmarket_cardnews_char_anchor(
            lang=lang,
            gender=gender,
            age_group_ko=age_group,
            persona_anchor_desc=anchor_desc,
            persona_cat=cat
        )

        # 2. ✍️ 제미나이 AI 100% 현지어 카드뉴스 카피라이팅 (제목, 부제, 뱃지, 3줄 불릿)
        generated_copy = self.copywriter.generate_kmarket_copy(
            lang=lang,
            theme=chosen_theme,
            persona=matched_persona
        )

        cards = []
        for idx in range(1, 6):
            copy_item = generated_copy[idx - 1] if len(generated_copy) >= idx else {}

            if idx == 1:
                # 🎬 1번 슬라이드: 보도블록 2인 실물 인계 (주인공 Person A + 상대방 Person B)
                image_prompt = build_kmarket_cardnews_scene_prompt(
                    slide_idx=1,
                    char=char_anchor,
                    scene_action=f"meeting outdoors on a clean Korean sidewalk near {target} to receive a free {item}",
                    item_name=item
                )
                negative_prompt = build_kmarket_cardnews_negative_prompt(lang=lang, slide_idx=1)
                card_type = "real_scene"
            elif idx == 2:
                # 🎬 2번 슬라이드: 아늑한 원룸 배치 & 만족 (1번 슬라이드와 동일 주인공 100%)
                image_prompt = build_kmarket_cardnews_scene_prompt(
                    slide_idx=2,
                    char=char_anchor,
                    scene_action=f"relaxing comfortably in student studio room with {item} placed neatly, feeling so relieved and proud of saving money",
                    item_name=item
                )
                negative_prompt = build_kmarket_cardnews_negative_prompt(lang=lang, slide_idx=2)
                card_type = "real_scene"
            elif idx == 3:
                # 📱 3번: K-Market 실제 0원 피드 스마트폰 목업
                image_prompt = "mockup_giveaway"
                negative_prompt = ""
                card_type = "mockup_giveaway"
            elif idx == 4:
                # 📱 4번: K-Market 실제 17개국어 번역 채팅 스마트폰 목업
                image_prompt = "mockup_translation"
                negative_prompt = ""
                card_type = "mockup_translation"
            else:
                # 🎬 5번 슬라이드: 자신감 넘치는 최종 추천 & CTA (1번, 2번 슬라이드와 동일 주인공 100%)
                image_prompt = build_kmarket_cardnews_scene_prompt(
                    slide_idx=5,
                    char=char_anchor,
                    scene_action=f"standing confidently in the furnished studio room with {item}, encouraging viewers to use K-Market 0 KRW giveaway",
                    item_name=item
                )
                negative_prompt = build_kmarket_cardnews_negative_prompt(lang=lang, slide_idx=5)
                card_type = "real_scene"

            cards.append({
                "slide_idx": idx,
                "card_type": card_type,
                "badge": copy_item.get("badge", f"STEP {idx}"),
                "title": copy_item.get("title", f"Step {idx} Title"),
                "subtitle": copy_item.get("subtitle", ""),
                "bullets": copy_item.get("bullets", []),
                "image_prompt": image_prompt,
                "negative_prompt": negative_prompt
            })

        return {
            "service_id": "kmarket",
            "lang": lang,
            "theme_name": theme_id,
            "theme_title": theme_name,
            "character_anchor": char_anchor,
            "episode_id": f"cardnews_kmarket_{lang}_{theme_id}_{random.randint(1000, 9999)}",
            "cards": cards
        }
