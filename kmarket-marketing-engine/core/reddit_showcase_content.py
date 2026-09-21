"""
📄 [Reddit Showcase Content Matrix]
- K-Market 및 EasyTax 공식 프로필 핀 포스트 및 자체 서브레딧용 고품질 영문 가이드 매트릭스
- 마크다운 서식, 공식 웹사이트 다이렉트 URL, 혜택 요약, 17개 언어 안내 포함
"""

from typing import Dict, Any
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


def get_easytax_pinned_showcase(target_url: str = "") -> Dict[str, Any]:
    """EasyTax (KTRS Tax) 공식 프로필 핀 포스트 (가이드 + 다이렉트 URL)"""
    url = target_url or BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")
    
    title = "💰 [Official Guide] Korea Expat Tax Refund & 90% SME Income Tax Exemption Calculator (Article 30, 3.3% Freelance, 5-Year Retroactive Filing)"
    
    body = f"""### Welcome to EasyTax (KTRS Expat Tax Advisory & Refund Portal)! 🇰🇷💼

Are you working, teaching, or studying in South Korea? You might be entitled to millions of KRW in overpaid income tax refunds from the National Tax Service (국세청 NTS)!

---

### 🎯 Who Can Claim & Major Tax Benefits:

1. **👨‍🏫 Native English Teachers & Professors (E-2, E-1 Visas)**
   * **Article 30 / Tax Treaty Exemption:** Up to **100% full income tax exemption for your first 2 years** in Korea (US, UK, Australia, South Africa, etc.).
   * If your school or Hagwon withheld income taxes, you can reclaim all of it!
2. **🏭 Foreign Workers in Small & Medium Enterprises (E-9, E-7, F-4 Visas)**
   * **90% SME Income Tax Reduction:** Qualifying manufacturing and SME employees can receive up to 90% reduction on earned income tax.
   * **5-Year Retroactive Filing (경정청구):** You can reclaim overpaid taxes from the past 5 consecutive years.
3. **🎓 International Students & Freelancers (D-2, D-4 Visas)**
   * **3.3% Withholding Tax Refund:** Claim back up to 100% of the 3.3% tax deducted from part-time jobs, translation gigs, or campus assistantships via May General Income Tax return (종합소득세).
4. **✈️ Departing Expats**
   * Lump-sum National Pension Refund & Final Year-end tax settlement assistance.

---

### 🔗 Official Free Simulation & Consultation:

* 🌐 **Free Estimated Refund Calculator:** [{url}]({url})
* 💬 **Search Keyword on Google:** `KTRS tax` or `EasyTax Korea`
* 📑 **100% Official NTS Guideline Compliant:** No advance fees — calculate your eligible amount in under 2 minutes.

---

*📌 Save/Upvote this post to review whenever your paycheck shows unexpected tax deductions or before your visa expires!*
"""
    return {
        "service_id": "easytax",
        "title": title,
        "body": body.strip(),
        "tags": ["EasyTax", "KoreaTaxRefund", "Article30", "E2Visa", "E9Visa", "ExpatTax"]
    }
