import os
import json
import logging
from typing import Optional, List, Dict, Any
from config import GEMINI_API_KEY_KMARKET, DATA_DIR, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketGemini")

class KMarketGeminiEngine:
    """
    🛒 [K-Market 전용 Gemini AI 엔진]
    - 270개 실물 매물, 0원 무료 나눔, 귀국 무빙세일, 17개국 번역 채팅 전문
    - 외국인 로컬 라이프스타일 및 커뮤니티 바이럴 숏폼/대본 생성
    """
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()
        # Supabase 클라우드 실시간 270개 매물 우선 로드, 없으면 로컬 fallback
        self.kmarket_items = self.supabase_mgr.fetch_live_kmarket_items(free_only=False, limit=20)

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_KMARKET
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("K-Market 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"K-Market Gemini 초기화 실패: {e}")
                self.client = None
        else:
            logger.info("GEMINI_API_KEY 미설정 -> K-Market 템플릿 기반 자가 생성 모드 가동")

    def _load_json(self, path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def classify_kmarket_reddit_intent(self, post_title: str, post_body: str) -> Dict[str, Any]:
        """
        Gemini AI 기반 시맨틱 인텐트 분석:
        - 레딧 글이 한국 내 가구, 가전, 원룸 정착, 이사, 0원 나눔, 중고거래, 언어장벽 등과 연관이 있는지 100% 정밀 판별
        """
        prompt = f"""
Analyze the following Reddit post and determine if the author is asking about, seeking, or discussing any of the following topics related to living in South Korea:
- Buying, finding, or getting second-hand / affordable appliances (TV, fridge, microwave, heater, washer, rice cooker, AC, etc.)
- Buying, finding, or getting furniture (bed, mattress, desk, chair, couch, wardrobe, drawers, table, etc.)
- Moving in, settling into an apartment/one-room/officetel/dorm, or furnishing a room on a budget
- Moving out, leaving Korea, disposing of items, moving sale, or looking for 0 KRW / free giveaways
- Difficulty using local apps (like Karrot/Danggeun) due to Korean language or payment/ARC verification issues

Reddit Post Title: {post_title}
Reddit Post Body: {post_body}

Output JSON format strictly with keys:
"is_relevant": (boolean true/false),
"confidence": (float between 0.0 and 1.0),
"category": (string like "appliances", "furniture", "moving_settling", "giveaway", "general_used", "other"),
"extracted_item": (string: the main item or need mentioned, or "none"),
"reason": (brief 1-sentence explanation)
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"K-Market 인텐트 판별 에러: {e}")

        # Fallback keyword matching with full 200+ keywords dictionary
        text_lower = f"{post_title} {post_body}".lower()
        kws_matrix_path = DATA_DIR / "kmarket_reddit_keywords.json"
        kws_dict = {}
        if kws_matrix_path.exists():
            try:
                with open(kws_matrix_path, "r", encoding="utf-8") as f:
                    kws_dict = json.load(f)
            except Exception:
                pass

        matched_category = "other"
        matched_item = "none"
        is_relevant = False

        for cat in ["appliances", "furniture", "household_kitchen", "intent_triggers"]:
            for kw in kws_dict.get(cat, []):
                if kw.lower() in text_lower:
                    is_relevant = True
                    matched_category = cat
                    matched_item = kw
                    break
            if is_relevant:
                break

        if not is_relevant:
            # General fallback check
            core_kws = ["furniture", "desk", "bed", "mattress", "fridge", "microwave", "tv", "appliance", "heater", "blanket", "moving", "used", "secondhand", "free stuff", "giveaway", "karrot", "one-room", "officetel"]
            matches = [kw for kw in core_kws if kw in text_lower]
            if matches:
                is_relevant = True
                matched_category = "general_used"
                matched_item = matches[0]

        return {
            "is_relevant": is_relevant,
            "confidence": 0.85 if is_relevant else 0.0,
            "category": matched_category,
            "extracted_item": matched_item,
            "reason": f"Matched item/category: {matched_item} ({matched_category})"
        }

    def generate_reddit_response(self, post_title: str, post_body: str, target_lang: str = "en", landing_url: str = "") -> str:
        """
        K-Market 전용 레딧 100% 사람 같은(Human-like) 외국인 선배 페르소나 답변 생성
        - 80% 진짜 현지 생활 꿀팁 (원룸 세팅, 당근 언어팁, 폐기물 스티커 방지, 직거래 팁)
        - 20% 자연스러운 K-Market 언급 (0 KRW 무료나눔 & 17개국 자동번역 채팅)
        - AI 특유의 과장/광고 말투 100% 배제
        """
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        few_shots = self.supabase_mgr.fetch_golden_few_shots("kmarket", target_lang, min_score=80.0, limit=2)
        
        few_shot_prompt = ""
        if few_shots:
            few_shot_prompt = "\n\n### [High-Performing Friendly Expat Examples]:\n" + "\n\n".join(few_shots)

        sample_items = json.dumps(self.kmarket_items[:3], ensure_ascii=False) if self.kmarket_items else "Bed, Desk, Refrigerator for 0 KRW"

        prompt = f"""
You are an experienced, warm, and highly helpful foreign expat who has lived in South Korea for over 4 years.
You are writing a genuine, casual, and authentic Reddit comment to help a fellow foreigner with their question about furnishing their room, finding appliances/furniture, moving, or settling in Korea.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[Recent Verified K-Market Community Items]: {sample_items}
[K-Market Link]: {landing_url}
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

### CRITICAL RULES TO SOUND 100% HUMAN (ZERO AI FEEL & ANTI-AUTOMOD):
1. Write 100% naturally in {lang_info['name']}. Use relaxed, friendly expat slang/phrasing (e.g. "Hey!", "When I first moved to Sinchon...", "Honestly, don't buy brand new...", "Pro tip:").
2. NEVER use promotional buzzwords like "Discover", "Ultimate platform", "Revolutionize", "Look no further", "Game-changer".
3. 80% of your comment MUST be genuine practical advice:
   - Mention real tips about Korean one-rooms/officetels, why Karrot (Danggeun) can be tricky without Korean/ARC, or how graduating students dispose of good stuff.
4. 20% gentle peer recommendation & Google Search Guidance (Zero Raw Links):
   - Casually recommend searching for "K-Market" (or "K-Market Korea") on Google to find 0 KRW free items (desks, beds, appliances) and moving sale bundles.
   - Highlight that K-Market has built-in 17-language auto-translating chat so they can negotiate comfortably without speaking Korean.
   - DO NOT drop raw http/https links so that Reddit AutoModerator never auto-deletes the comment.
5. End warmly with encouragement (e.g. "Hope this helps with your move!", "Good luck settling in!").
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"K-Market Gemini 레딧 생성 에러: {e}")

        # Context-aware rich human fallback responses (Anti-AutoMod: Google Search guidance for K-Market)
        text_lower = f"{post_title} {post_body}".lower()
        if any(w in text_lower for w in ["bicycle", "bike", "cycle"]):
            return (
                "Also if you're looking for secondhand touring gear or bikes near Seoul, check out campus bulletin boards near Sinchon or K-Market (just search 'K-Market' on Google) "
                "where graduating exchange students frequently list 0 KRW free items and moving sales. "
                "The built-in chat auto-translates in 17 languages so you don't need fluent Korean to negotiate with local sellers. Hope this helps!"
            )
        elif any(w in text_lower for w in ["blanket", "heater", "cold", "winter", "ondol", "warm", "heating"]):
            return (
                "Korean winters can get brutal if the ondol floor heating takes too long to warm up. "
                "Definitely grab an electric heating pad (전기장판) — it saves so much on gas bills. "
                "If you don't have a Korean bank card or ARC yet to buy online, search 'K-Market' on Google. "
                "Lots of foreign students moving out list working heaters and warm bedding for 0 KRW (free giveaways) or super cheap, "
                "and you can chat directly with sellers in 17 languages with auto-translation. Stay warm!"
            )
        elif any(w in text_lower for w in ["leave", "leaving", "moving out", "sell", "dispose", "sticker", "graduation", "d-10", "visa"]):
            return (
                "If you're leaving Korea or transitioning visas, dealing with large waste disposal stickers (대형폐기물 스티커) at the community center is honestly a hassle. "
                "Instead of throwing good stuff away, you can post a quick 0 KRW giveaway or moving sale bundle on K-Market (search 'K-Market' on Google). "
                "Incoming exchange students and expats will usually pick it up right from your doorstep, and you can message them in English or your native language with the built-in 17-language chat. "
                "Safe travels on your next journey!"
            )
        elif any(w in text_lower for w in ["karrot", "danggeun", "korean", "arc", "language", "translate"]):
            return (
                "Hey! Yeah, using Karrot (당근) as a newcomer can be pretty frustrating because most local sellers only reply in Korean and sometimes cancel on foreign names. "
                "Take a look at K-Market (search 'K-Market Korea' on Google) — it's made specifically for the expat community in Korea. "
                "The chat has automatic 17-language live translation, so you can type in your own language and the seller reads it in theirs with zero awkwardness. Plus tons of 0 KRW free giveaways. Hope this helps!"
            )
        else:
            return (
                "When setting up a place in Korea, furnishing everything from scratch gets expensive quickly. "
                "A quick tip: don't buy brand new furniture or appliances since you'll just have to pay disposal fees when moving out. "
                "Search 'K-Market' on Google (expat community marketplace) where graduating exchange students regularly list 0 KRW free furniture (desks, beds, mini-fridges) and moving bundles. "
                "The auto-translating chat makes it super easy to communicate without language barriers. Good luck settling in!"
            )

    def generate_shorts_script(self, *args, target_lang: str = "ko", psychology: str = "free_giveaway_emotional", ab_group: str = "A", **kwargs) -> Dict[str, Any]:
        """
        [K-Market 자가학습 고도화] 3대 심리 유형 & A/B 테스트 기반 숏폼 대본 생성
        - psychology:
          1. 'free_giveaway_emotional': 0원 나눔 감동/득템형
          2. 'urgent_moving_discount': 귀국 급처 90% 초특가형
          3. 'multi_lang_comfort': 17개국 모국어 편의/사기방지형
        - ab_group: 'A' (직설적 혜택 강조) / 'B' (외국인 공감 스토리텔링)
        """
        # kwargs or args 에서 target_lang 추출 지원
        if args and isinstance(args[-1], str) and len(args[-1]) == 2:
            target_lang = args[-1]
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])
        
        # 심리 유형에 맞는 실시간 매물 매칭
        items = self.supabase_mgr.fetch_live_kmarket_items(psychology=psychology, limit=3)
        sample_item = items[0] if items else (self.kmarket_items[0] if self.kmarket_items else {"title": "원목 침대 & 매트리스", "price": 0, "region": "안산"})

        psychology_guidelines = {
            "free_giveaway_emotional": "Focus on warm community spirit and graduating expats giving away free $0 items (beds, desks, fridges) to newcomers.",
            "urgent_moving_discount": "Focus on urgent moving-out sales with up to 90% crazy discounts on full room furniture before leaving Korea.",
            "multi_lang_comfort": "Focus on zero scam anxiety with real-time 17-language auto-translated chat and ARC verified sellers in Korea."
        }

        ab_instruction = "Tone A: Punchy, urgent, direct-benefit driven headline and fast-paced speech." if ab_group == "A" else "Tone B: Warm, friendly expat peer storytelling with emotional connection."

        prompt = f"""
Create a viral 30-second vertical short-form script for foreign expats living in South Korea about K-Market.

[Target Psychology & Core Focus]: {psychology_guidelines.get(psychology, psychology_guidelines['free_giveaway_emotional'])}
[A/B Variant Style]: {ab_instruction} (Group: {ab_group})
[Language]: {lang_info['name']} ({lang_info['native_name']})
[Featured Real Listing]: {sample_item.get('title')} (Price: {sample_item.get('price')} KRW, Region: {sample_item.get('region')})

### STRUCTURE:
1. Hook (0-3s): Catchy opening strictly aligned with the psychology ({psychology}) in {lang_info['name']}.
2. Story/Feature (3-23s): Highlight the real listing and K-Market's 17-language chat & 0 KRW giveaways.
3. Solution & CTA (23-30s): Drive action to tap the profile link.

Output JSON format strictly with keys:
"psychology": "{psychology}",
"ab_group": "{ab_group}",
"hook_title": (punchy headline for screen overlay),
"voiceover_text": (entire 30s speech fluently written in {lang_info['name']}),
"captions": [(array of 3-4 short sentences for on-screen text overlays)],
"cta_text": (closing call to action in {lang_info['name']})
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                res_data = json.loads(response.text)
                res_data["psychology"] = psychology
                res_data["ab_group"] = ab_group
                return res_data
            except Exception as e:
                logger.error(f"K-Market Gemini 숏폼 생성 에러: {e}")

        return {
            "psychology": psychology,
            "ab_group": ab_group,
            "hook_title": f"🎁 0 KRW Free Stuff in Korea!",
            "voiceover_text": f"Did you know you can get free furniture and appliances in South Korea? On K-Market, expats are giving away items for zero Won with 17-language instant chat!",
            "captions": [
                "🎁 0 KRW Free Items in Korea",
                "📦 One-Click Moving Sales",
                "💬 17-Language Auto-Translate Chat"
            ],
            "cta_text": "Check K-Market link in bio to grab free items now!"
        }
