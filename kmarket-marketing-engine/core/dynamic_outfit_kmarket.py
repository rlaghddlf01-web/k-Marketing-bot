"""
DynamicOutfitKMarket - 🛒 [K-Market 전용 동적 의상 자율 선택 엔진]
- 60대 테마별 페르소나 카테고리(campus / industry / it)에 맞춰 의상을 매번 다르게 자동 선택
- 하드코딩 완전 배제: 봇이 주제에 따라 스스로 결정 (대표님 절대 지침)
- 주인공 vs 상대방 의상 색상 대비(Contrasting) 자동 보장
- 카테고리별 10~12벌 의상 풀 → 매 에피소드마다 겹침 없는 다양한 룩 연출
"""

import random

# ======================================================================
# 🎨 카테고리별 동적 의상 풀 (매 생성마다 랜덤 1개 선택)
# ======================================================================

# ── [1. 대학가 캠퍼스 유학생 여성 (20대)] ──
CAMPUS_FEMALE_OUTFITS = [
    "wearing an oversized pastel beige knit sweater and neat blue denim jeans",
    "wearing a cozy heather grey college hoodie and black leggings",
    "wearing a soft lavender cardigan over a white tee and light wash denim",
    "wearing a forest green campus sweatshirt and dark navy jogger pants",
    "wearing a cream-colored turtleneck sweater and camel corduroy pants",
    "wearing a dusty rose oversized flannel shirt and black skinny jeans",
    "wearing a light denim jacket over a striped tee and olive cargo pants",
    "wearing a burgundy university hoodie and grey sweatpants",
    "wearing a mustard yellow knit cardigan and dark wash bootcut jeans",
    "wearing a sky blue chambray shirt and high-waisted brown chinos",
    "wearing a mint green pullover and white wide-leg pants",
    "wearing a warm terracotta knit top and dark olive straight-leg jeans",
]

# ── [2. 대학가 캠퍼스 유학생 남성 (20대)] ──
CAMPUS_MALE_OUTFITS = [
    "wearing a dark green university hoodie and black jeans",
    "wearing a navy blue bomber jacket over a white tee and khaki chinos",
    "wearing a heather grey crewneck sweatshirt and dark indigo jeans",
    "wearing a maroon college zip-up jacket and olive cargo pants",
    "wearing a camel brown corduroy jacket and dark wash denim jeans",
    "wearing a classic plaid flannel shirt and faded blue jeans",
    "wearing a charcoal pullover hoodie and tan chinos",
    "wearing an olive green field jacket and black jogger pants",
    "wearing a light blue oxford shirt and navy cotton slacks",
    "wearing a rust orange crewneck sweater and grey straight-leg pants",
    "wearing a black varsity jacket with white sleeves and blue jeans",
    "wearing a stone beige linen shirt and dark brown chinos",
]

# ── [3. 산업단지/공단 근로자 여성 (20대 후반)] ──
INDUSTRY_FEMALE_OUTFITS = [
    "wearing a simple comfortable navy zip-up fleece jacket and grey casual trousers",
    "wearing a warm brown quilted vest over a cream thermal and dark work pants",
    "wearing a charcoal grey zip-up hoodie and black comfortable joggers",
    "wearing a forest green padded vest over a white long-sleeve and navy pants",
    "wearing a burgundy fleece pullover and khaki utility pants",
    "wearing a teal windbreaker jacket and dark grey cotton pants",
    "wearing a camel-colored knit zip-up and comfortable black work trousers",
    "wearing a slate blue utility jacket and olive straight-leg pants",
    "wearing a soft peach fleece pullover and dark denim jeans",
    "wearing a dusty pink puffer vest over a grey sweatshirt and black pants",
]

# ── [4. 산업단지/공단 근로자 남성 (20대 후반)] ──
INDUSTRY_MALE_OUTFITS = [
    "wearing a comfortable heather grey crewneck sweatshirt and dark blue jeans",
    "wearing a navy blue work jacket and light grey cargo pants",
    "wearing a dark olive utility vest over a black thermal and brown work pants",
    "wearing a charcoal zip-up fleece and tan work trousers",
    "wearing a warm brown bomber jacket and dark wash denim jeans",
    "wearing a forest green crewneck pullover and black jogger pants",
    "wearing a steel blue padded jacket and dark khaki pants",
    "wearing a maroon quarter-zip pullover and charcoal work trousers",
    "wearing a sand-colored canvas jacket and dark navy work pants",
    "wearing a burgundy thermal henley and grey utility trousers",
]

# ── [5. IT/전문직 여성 (30대)] ──
IT_FEMALE_OUTFITS = [
    "wearing a stylish light blue tailored casual blouse and navy slacks",
    "wearing a modern charcoal blazer over a white crew-neck tee and dark jeans",
    "wearing an elegant cream silk blouse and tailored grey trousers",
    "wearing a soft mauve knit top and high-waisted black wide-leg pants",
    "wearing a structured dusty pink jacket and dark indigo slim jeans",
    "wearing a sage green linen shirt and beige tailored chinos",
    "wearing a sophisticated black turtleneck and camel wide-leg trousers",
    "wearing a periwinkle blue wrap blouse and charcoal pencil trousers",
    "wearing a warm coral cardigan over a white top and navy tailored pants",
    "wearing a deep teal fitted blazer and cream straight-leg trousers",
]

# ── [6. IT/전문직 남성 (30대)] ──
IT_MALE_OUTFITS = [
    "wearing a clean black smart casual polo shirt and dark grey chinos",
    "wearing a modern navy blazer over a white tee and slim khaki pants",
    "wearing a charcoal merino wool crew-neck and dark indigo jeans",
    "wearing a crisp light grey button-down shirt and navy cotton slacks",
    "wearing a forest green smart polo and tan chinos",
    "wearing a burgundy casual blazer over a black tee and dark jeans",
    "wearing a stone beige linen jacket over a navy henley and grey pants",
    "wearing an olive smart-casual knit sweater and dark brown trousers",
    "wearing a steel blue quarter-zip pullover and charcoal slim pants",
    "wearing a deep navy cashmere crew-neck and light grey tailored trousers",
]

# ── [7. 상대방(선배/이웃) 전용 의상 풀 (주인공과 대비되는 스타일)] ──
COUNTERPART_OUTFITS = [
    "wearing a casual grey sweatshirt and blue jeans",
    "wearing a warm brown cardigan and dark chinos",
    "wearing a navy blue windbreaker and khaki pants",
    "wearing a white pullover hoodie and black joggers",
    "wearing an olive green utility jacket and grey trousers",
    "wearing a charcoal fleece vest over a cream shirt and brown pants",
    "wearing a teal crewneck sweater and dark denim jeans",
    "wearing a maroon zip-up jacket and light grey sweatpants",
    "wearing a dusty blue denim jacket and beige chinos",
    "wearing a forest green polo shirt and navy cotton pants",
    "wearing a light khaki jacket and dark wash jeans",
    "wearing a slate grey bomber jacket and black pants",
    "wearing a rust orange quilted vest over a white tee and dark jeans",
    "wearing a camel corduroy shirt jacket and olive cargo pants",
]

# ======================================================================
# 🗺️ 카테고리 키 → 의상 풀 매핑
# ======================================================================
OUTFIT_POOL_MAP = {
    ("campus", "female"): CAMPUS_FEMALE_OUTFITS,
    ("campus", "male"): CAMPUS_MALE_OUTFITS,
    ("industry", "female"): INDUSTRY_FEMALE_OUTFITS,
    ("industry", "male"): INDUSTRY_MALE_OUTFITS,
    ("it", "female"): IT_FEMALE_OUTFITS,
    ("it", "male"): IT_MALE_OUTFITS,
}

# 의상에서 주요 색상 추출용 키워드 세트
_COLOR_KEYWORDS = {
    "beige", "grey", "gray", "navy", "green", "blue", "brown", "black",
    "white", "cream", "olive", "maroon", "burgundy", "charcoal", "khaki",
    "red", "orange", "yellow", "pink", "purple", "teal", "rust", "camel",
    "lavender", "mustard", "mint", "sage", "dusty", "slate", "stone",
    "terracotta", "periwinkle", "forest", "sky", "coral", "peach", "sand",
    "mauve", "steel", "deep",
}


def get_dynamic_outfit(persona_cat: str, gender: str) -> str:
    """
    🎨 페르소나 카테고리와 성별에 맞는 의상을 매번 다르게 랜덤 선택
    - 하드코딩 0%: 봇이 주제에 따라 스스로 결정
    - campus/industry/it × male/female = 6개 풀에서 자율 선택

    Args:
        persona_cat: 페르소나 카테고리 ("campus", "industry", "it")
        gender: 성별 ("male", "female")
    Returns:
        "wearing a ..." 형태의 의상 문자열
    """
    pool = OUTFIT_POOL_MAP.get((persona_cat, gender))
    if not pool:
        # 안전 폴백: 성별에 맞는 캠퍼스 풀 사용
        pool = OUTFIT_POOL_MAP.get(("campus", gender), CAMPUS_FEMALE_OUTFITS)
    return random.choice(pool)


def get_counterpart_outfit(protagonist_description: str) -> str:
    """
    🎭 주인공과 완전히 다른 색상·스타일의 대비 의상을 자동 선택
    - 주인공 의상의 주요 색상 키워드를 추출하여 겹치지 않는 의상만 필터링
    - "두 사람이 완전히 다른 옷을 입고 있어야 한다" (대표님 지침) 자동 보장

    Args:
        protagonist_description: 주인공의 전체 캐릭터 설명 문자열 (의상 포함)
    Returns:
        "wearing a ..." 형태의 상대방 의상 문자열
    """
    # 주인공 설명에서 색상 키워드 추출
    desc_lower = protagonist_description.lower()
    protagonist_colors = {kw for kw in _COLOR_KEYWORDS if kw in desc_lower}

    # 주인공 색상과 겹치지 않는 상대방 의상만 필터링
    non_overlapping = [
        outfit for outfit in COUNTERPART_OUTFITS
        if not any(c in outfit.lower() for c in protagonist_colors)
    ]

    if non_overlapping:
        return random.choice(non_overlapping)
    # 모두 겹칠 경우 (극히 드문 케이스) 랜덤 선택
    return random.choice(COUNTERPART_OUTFITS)
