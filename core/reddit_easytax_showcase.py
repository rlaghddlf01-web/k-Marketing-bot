"""
💰 [EasyTax 전용 Reddit Showcase Content Matrix]
- 100% EasyTax 전용 독립 모듈 (K-Market과 완전 분리)
- 조특법 제30조 & 90% 중기 소득세 감면 & D-2 3.3% 환급 영문 가이드 및 다이렉트 URL
"""

from typing import Dict, Any
from config import BASE_URLS

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
