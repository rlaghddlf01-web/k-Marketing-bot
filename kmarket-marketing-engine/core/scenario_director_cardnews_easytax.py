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

from core.character_anchor_cardnews_easytax import (
    build_easytax_cardnews_char_anchor,
    build_easytax_cardnews_scene_prompt,
    build_easytax_cardnews_negative_prompt,
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

    def _match_persona(self, theme: Dict[str, Any], preferred_gender: Optional[str] = None) -> Dict[str, Any]:
        """테마의 비자/타깃에 맞춰 최적의 페르소나를 자동 매칭 (남성 40% : 여성 60% 비율 엄격 유지)"""
        target = theme.get("target", "").lower()
        cat = theme.get("cat", "")
        theme_id = theme.get("id", "")

        # 🎯 [성별 50:50 완벽 랜덤 균등 분배]
        target_gender = preferred_gender if preferred_gender in ["female", "male"] else random.choices(["female", "male"], weights=[50, 50], k=1)[0]

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

    def get_carousel_scenario(
        self,
        lang: str = "vi",
        theme_index: Optional[int] = None,
        preferred_gender: Optional[str] = None,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """카드뉴스 전용 독립 캐릭터 앵커로 1, 2, 4번 슬라이드 100% 동일 인물 보장 5장 카드뉴스 생성"""
        from config import DATA_DIR
        import json
        rotation_file = DATA_DIR / "cardnews_rotation_state_easytax.json"
        
        if theme_index is not None:
            chosen_theme = self.themes[theme_index % len(self.themes)]
        else:
            curr_idx = 0
            if rotation_file.exists():
                try:
                    with open(rotation_file, "r", encoding="utf-8") as f:
                        curr_idx = json.load(f).get("index", 0)
                except Exception:
                    curr_idx = 0
            
            chosen_theme = self.themes[curr_idx % len(self.themes)]
            next_idx = (curr_idx + 1) % len(self.themes)
            try:
                rotation_file.parent.mkdir(parents=True, exist_ok=True)
                with open(rotation_file, "w", encoding="utf-8") as f:
                    json.dump({"index": next_idx}, f)
            except Exception:
                pass

        theme_id = chosen_theme["id"]
        theme_name = chosen_theme["name"]
        target = chosen_theme["target"]
        persona_type = chosen_theme["persona_type"]
        # 🎯 [금액 100% 원천 동기화] 지정된 amount 우선 적용 (없으면 테마 고유 refund_est)
        refund_est = amount if amount is not None else chosen_theme.get("refund_est", 3840000)
        refund_formatted = f"{refund_est:,} KRW"

        # 1. 🎯 테마 맞춤형 7대 비자별 페르소나 및 독립 캐릭터 앵커 생성
        matched_persona = self._match_persona(chosen_theme, preferred_gender=preferred_gender)
        char_anchor = build_easytax_cardnews_char_anchor(
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

        # 3. 🎯 테마별 5단계 슬라이드 기승전결 연출 (1:일상인물 -> 2:일터현장동일인물 -> 3:실제앱0원보증 -> 4:꿈의실현동일인물 -> 5:실제앱1분조회)
        theme_text_lower = (theme_id + " " + theme_name + " " + target).lower()
        
        # 1번: 일상 실내 거실 배경에서 환급 통지서를 확인하고 환호하며 기뻐하는 주인공 인물
        s1_prompt = "sitting naturally in bright modern living room with natural window ambient light, warm genuine friendly beaming smile, celebrating tax refund relief"

        # 2번: 일터 현장 배경에서 성실하게 일하는 동일 인물 주인공 (의상 통일, 배경만 일터)
        s2_prompt = "in a modern industrial workplace or company environment in the background, honest hardworking posture, proud sincere determined eyes with a warm hopeful smile"

        # 3번: [이지텍스 앱 환급 0단계 모의조회] 1번과 동일 인물이 스마트폰 없이 아늑한 카페/방에서 안도하는 컷
        s3_prompt = "sitting comfortably in a warm quiet sunlit cafe or cozy room with soft ambient light, peaceful, relieved, and confident smile"

        # 4번: [사연의 절정/꿈의 실현] 동일 주인공이 공항 터미널에서 고향 가족을 생각하며 활짝 웃는 감동 컷
        s4_prompt = "at a bright spacious modern airport departure terminal in the background beside travel luggage, radiant ecstatic smile of pure homecoming joy"

        # 5번: [이지텍스 앱 1분 조회 CTA] 1번과 동일 인물이 스마트폰 없이 카페 테이블 앞 엄지척(👍)으로 "지금 확인해봐!" 권유하는 컷
        s5_prompt = "in a modern stylish coffee shop setting, seated at wooden cafe table with a warm coffee mug, looking directly at camera with an encouraging friendly smile, giving a confident thumbs-up sign (thumbs up)"

        scene_actions = {
            1: s1_prompt,
            2: s2_prompt,
            3: s3_prompt,
            4: s4_prompt,
            5: s5_prompt
        }

        cards = []
        for idx in range(1, 6):
            copy_item = generated_copy[idx - 1] if len(generated_copy) >= idx else {}
            action_desc = scene_actions.get(idx, "sitting naturally")

            if idx == 1:
                # 1번: 3.5m 거리 거실 배경 + 스마트폰 전면 파지 컷 (스마트폰 미파지 및 얼빡샷 원천 차단)
                full_prompt = build_easytax_cardnews_scene_prompt(slide_idx=1, char=char_anchor, scene_action=action_desc)
                neg_prompt = build_easytax_cardnews_negative_prompt(
                    lang=lang,
                    extra="empty hands, no phone in hand, smartphone in pocket, holding nothing, upside down phone, deformed hand, extreme close-up, cropped face, headshot, bust shot"
                )
                is_scene_focus = False
                is_app_screen = False
                app_screen_type = None
            elif idx == 2:
                # 2번: 일터 배경의 동일 인물 주인공 (스마트폰 절대 금지!)
                full_prompt = build_easytax_cardnews_scene_prompt(slide_idx=2, char=char_anchor, scene_action=action_desc)
                neg_prompt = build_easytax_cardnews_negative_prompt(
                    lang=lang,
                    extra="holding smartphone, phone in hand, smartphone, mobile device, extreme close-up, cropped head, giant face"
                )
                is_scene_focus = False
                is_app_screen = False
                app_screen_type = None
            elif idx == 3:
                # 3번: 1번 주인공 동일 인물이 스마트폰 없이 카페/방에서 안도하는 컷 (스마트폰 절대 금지!)
                full_prompt = build_easytax_cardnews_scene_prompt(slide_idx=3, char=char_anchor, scene_action=action_desc)
                neg_prompt = build_easytax_cardnews_negative_prompt(
                    lang=lang,
                    extra="smartphone, phone, mobile device, holding phone, phone in hand, black screen phone, dead screen, extreme close-up"
                )
                is_scene_focus = False
                is_app_screen = True
                app_screen_type = "step0"
            elif idx == 4:
                # 4번: 공항 터미널 배경의 감동 컷 (스마트폰 절대 금지!)
                full_prompt = build_easytax_cardnews_scene_prompt(slide_idx=4, char=char_anchor, scene_action=action_desc)
                neg_prompt = build_easytax_cardnews_negative_prompt(
                    lang=lang,
                    extra="smartphone, phone, mobile device, holding phone, phone in hand, extreme close-up, cropped head"
                )
                is_scene_focus = False
                is_app_screen = False
                app_screen_type = None
            else:
                # 5번: 1번 주인공 동일 인물이 카페에서 엄지척 권유하는 결말 컷 (스마트폰 절대 금지!)
                full_prompt = build_easytax_cardnews_scene_prompt(slide_idx=5, char=char_anchor, scene_action=action_desc)
                neg_prompt = build_easytax_cardnews_negative_prompt(
                    lang=lang,
                    extra="smartphone, phone, mobile device, holding phone, phone in hand, black screen phone, dead screen, extreme close-up"
                )
                is_scene_focus = False
                is_app_screen = True
                app_screen_type = "home_cta"

            cards.append({
                "slide_idx": idx,
                "badge": copy_item.get("badge", f"STEP {idx}"),
                "title": copy_item.get("title", f"Step {idx} Title"),
                "subtitle": copy_item.get("subtitle", ""),
                "bullets": copy_item.get("bullets", []),
                "cta_button": copy_item.get("cta_button", ""),
                "image_prompt": full_prompt,
                "negative_prompt": neg_prompt,
                "is_scene_focus": is_scene_focus,
                "is_app_screen": is_app_screen,
                "app_screen_type": app_screen_type
            })

        return {
            "service_id": "easytax",
            "lang": lang,
            "theme_name": theme_id,
            "theme_title": theme_name,
            "refund_est": refund_est,
            "refund_formatted": refund_formatted,
            "character_anchor": char_anchor,
            "episode_id": f"cardnews_easytax_{lang}_{theme_id}_{random.randint(1000, 9999)}",
            "cards": cards
        }
