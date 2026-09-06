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
        """60대 세무 테마 중 1개를 순환 선택하고 제미나이 100% 현지어 카피라이팅으로 5장 카드뉴스 생성"""
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

        # 3. 🎯 테마별 5단계 슬라이드 기승전결 다채로운 연출 (1:일상인물 -> 2:일터현장동일인물 -> 3:실제앱0원보증 -> 4:비행기사연 -> 5:실제앱1분조회)
        theme_text_lower = (theme_id + " " + theme_name + " " + target).lower()
        
        # 1번: 일상 실내(카페/방)에서 환급 알림을 받고 환호하며 기뻐하는 주인공 인물
        s1_prompt = (
            f"cinematic authentic portrait, sitting relaxed and happily in cozy cafe or bright modern living room, "
            f"warm natural sunlight pouring in, ecstatic overjoyed facial expression with radiant beaming smile, "
            f"one arm welcoming towards camera celebrating financial breakthrough and huge tax refund relief, "
            f"warm cinematic portrait lighting, highly detailed skin texture, 8k masterpiece"
        )

        # 2번: 치열한 작업 현장(공장/농장/물류) 속 작업복을 착용하고 땀 흘리며 일하는 동일 인물 주인공
        if any(w in theme_text_lower for w in ["flight", "vacation", "비행기", "여행", "귀국"]):
            s2_prompt = (
                f"wearing realistic industrial factory work uniform or agricultural work clothes with safety gear, "
                f"working diligently amidst busy Korean manufacturing factory assembly line or greenhouse, "
                f"sweat glistening on brow, honest hardworking authentic expression, proud determined eyes, "
                f"cinematic industrial lighting, depth of field showing working machines in background"
            )
        elif any(w in theme_text_lower for w in ["parent", "house", "송금", "가족", "효도"]):
            s2_prompt = (
                f"wearing authentic Korean factory work jacket, taking a brief respectful breath during night shift, "
                f"gentle sincere thoughtful face, wiping sweat with honest hardworking posture, factory background with machinery"
            )
        elif any(w in theme_text_lower for w in ["tuition", "student", "등록금", "유학", "d-2", "알바"]):
            s2_prompt = (
                f"wearing convenience store / restaurant work apron or delivery jacket, honest student working evening shift, "
                f"tired but determined eyes, genuine hardworking student in Korea, authentic atmospheric lighting"
            )
        else:
            s2_prompt = (
                f"wearing industrial work clothes in realistic Korean manufacturing or logistics warehouse, "
                f"honest sincere expression of dedicated foreign worker, holding tools, hardworking sweat, cinematic natural lighting"
            )

        # 3번: [이지텍스 앱 환급 0단계 모의조회] 모던한 금융 오피스 원목 데스크 실사 배경 (스마트폰 인셋 탑재)
        s3_prompt = (
            "clean minimalist modern finance office wooden desk background, smooth warm oak wood grain surface, "
            "elegant luxury pen, clean glass paperweight, warm ceramic cup of coffee, gentle natural window sunlight, "
            "clean empty center desk surface ready for smartphone display, 8k commercial still-life photograph"
        )

        # 4번: [사연의 절정/꿈의 실현 현장 컷] 인물 얼굴 대신 사연에 맞는 비행기/송금/공항/학비 리얼 현장 사진
        if any(w in theme_text_lower for w in ["flight", "vacation", "비행기", "여행", "귀국", "고향"]):
            s4_prompt = (
                "cinematic photorealistic shot of an airplane wing flying high above magnificent sunset clouds through passenger window, "
                "warm golden glow across fluffy sea of clouds, pure wanderlust and homecoming joy, hyper-realistic 8k masterpiece"
            )
        elif any(w in theme_text_lower for w in ["parent", "house", "송금", "가족", "효도"]):
            s4_prompt = (
                "cinematic close-up shot of a cozy family living room table with warm cup of tea and lovely family photo, "
                "international money remittance receipt resting peacefully in warm golden hour afternoon sunlight, 8k photograph"
            )
        elif any(w in theme_text_lower for w in ["tuition", "student", "등록금", "유학", "d-2", "알바"]):
            s4_prompt = (
                "cinematic beautiful shot of Korean university campus walkway in autumn with golden leaves, "
                "student desk with textbooks and official university tuition payment receipt stamped paid, bright hopeful morning sunlight, 8k photograph"
            )
        else:
            s4_prompt = (
                "cinematic shot of a packed travel luggage suitcase with Korean gifts, flight ticket and passport on the table, "
                "bright morning sunlight pouring through the window, feeling of going back home triumphantly, 8k photograph"
            )

        # 5번: [이지텍스 앱 1분 조회 CTA] 따뜻한 홈/오피스 데스크 실사 배경 (스마트폰 인셋 탑재)
        s5_prompt = (
            "modern cozy wooden desk surface with warm ambient lighting, small green potted succulent plant on side, "
            "inviting ceramic coffee mug, blurred indoor cozy living room background, clean empty center desk ready for smartphone display, 8k commercial photograph"
        )

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
            action_desc = scene_actions.get(idx, "working in workplace")

            if idx == 1:
                # 1번: 일상 실내 주인공 (인물 락 + 스마트폰 통지 인셋)
                full_prompt = build_easytax_scene_prompt(scene_idx=1, char=char_anchor, scene_action=action_desc)
                neg_prompt = f"upside down phone, deformed hand holding phone, bad anatomy, ugly, blurry, 3d render, cartoon, {LANG_NEGATIVE_ETHNIC.get(lang, '')}"
                is_scene_focus = False
                is_app_screen = False
                app_screen_type = None
            elif idx == 2:
                # 2번: 일터 현장의 동일 인물 주인공 (Zero-RAM 인물 락)
                full_prompt = build_easytax_scene_prompt(scene_idx=2, char=char_anchor, scene_action=action_desc)
                neg_prompt = f"bad anatomy, extra limbs, ugly, blurry, 3d render, cartoon, suit, tie, luxury clothes, {LANG_NEGATIVE_ETHNIC.get(lang, '')}"
                is_scene_focus = False
                is_app_screen = False
                app_screen_type = None
            elif idx == 3:
                # 3번: 실제 이지텍스 앱 화면 (환급 0단계 모의 조회)
                full_prompt = f"{action_desc}, master commercial product photography, 8k"
                neg_prompt = "human face close-up, people, distorted desk, blurry, 3d render, cartoon, papers with writing, text on paper, handwriting, gibberish letters, messy papers, documents"
                is_scene_focus = True
                is_app_screen = True
                app_screen_type = "step0"
            elif idx == 4:
                # 4번: 사연의 결실 현장 컷 (비행기 노을 등)
                full_prompt = f"{action_desc}, 4k ultra realistic photograph, master cinematographic lighting, 8k"
                neg_prompt = "human face close-up, ugly, blurry, 3d render, cartoon, deformed objects"
                is_scene_focus = True
                is_app_screen = False
                app_screen_type = None
            else:
                # 5번: 실제 이지텍스 앱 메인 화면 (1분 조회 시작 CTA)
                full_prompt = f"{action_desc}, master commercial product photography, 8k"
                neg_prompt = "human face close-up, people, ugly, blurry, 3d render, cartoon, laptop screen text, screens with text, papers with writing, messy desk, gibberish letters"
                is_scene_focus = True
                is_app_screen = True
                app_screen_type = "home_cta"

            cards.append({
                "slide_idx": idx,
                "badge": copy_item.get("badge", f"STEP {idx}"),
                "title": copy_item.get("title", f"Step {idx} Title"),
                "subtitle": copy_item.get("subtitle", ""),
                "bullets": copy_item.get("bullets", []),
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
            "character_anchor": char_anchor,
            "episode_id": f"cardnews_easytax_{lang}_{theme_id}_{random.randint(1000, 9999)}",
            "cards": cards
        }
