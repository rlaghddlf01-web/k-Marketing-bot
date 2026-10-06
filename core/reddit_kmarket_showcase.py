"""
🛒 [K-Market 전용 Reddit Showcase Content Matrix]
- 100% K-Market 전용 독립 모듈 (EasyTax와 완전 분리)
- 17개 언어 자동번역 마켓 & $0 무료나눔 & 귀국 무빙세일 영문 가이드 및 다이렉트 URL
"""

from typing import Dict, List
from config import BASE_URLS

def get_kmarket_pinned_showcase(target_url: str = "") -> Dict[str, str]:
    """K-Market 공식 프로필 핀 포스트 (가이드 + 다이렉트 URL)"""
    url = target_url or BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")
    
    title = "🛒 [Official Guide] K-Market: $0 Free Giveaways & Expat Secondhand Marketplace in Korea (Auto-translated in 17 Languages)"
    
    body = f"""### Welcome to K-Market (Korea Expat Marketplace & Community)! 🇰🇷

Moving to, living in, or leaving South Korea? **K-Market** is the dedicated, foreigner-friendly community marketplace designed to eliminate language barriers and waste disposal hassles.

---

### 🌟 Key Highlights & Features:

* **🌍 17 Languages Real-Time Auto-Translation**
  * Chat and trade seamlessly with other international students, expats, and Korean locals in English, Vietnamese (Tiếng Việt), Chinese (中文), Russian (Русский), Uzbek (O'zbek), Mongolian (Монгол), Thai (ไทย), and more.
* **🎁 $0 Free Pass-Down & Giveaway Hub**
  * Graduating or moving out? Don't pay expensive bulky waste disposal sticker fees (대형폐기물 스티커). Easily pass down desks, chairs, microwaves, beds, and refrigerators to arriving students for free!
* **📦 Expat Moving Sales & Secondhand Deals**
  * Find affordable studio (원룸) furniture, electronics, textbooks, and daily necessities directly from fellow expats nearby.
* **🛡️ No Complex Korean ID / Domestic Mobile Verification Barrier**
  * Designed specifically for foreign residents, language students, teachers, and international workers.

---

### 🔗 Quick Access & Official Links:

* 🌐 **Official Web Platform:** [{url}]({url})
* 💬 **Search Keyword on Google:** `k-market korea` or `KTRS market`
* 📱 **Mobile & Desktop Friendly:** Works instantly in any browser without complicated app store installations.

---

*💡 Bookmark this post or visit our official site whenever you need affordable home essentials or need to clear out your apartment before leaving Korea!*
"""
    return {
        "service_id": "kmarket",
        "title": title,
        "body": body.strip(),
        "tags": ["KMarket", "ExpatLife", "LivingInKorea", "FreeGiveaway", "SecondhandKorea"]
    }
