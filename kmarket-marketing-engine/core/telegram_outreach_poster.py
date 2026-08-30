"""
TelegramOutreachPoster - 📢 타 텔레그램 공개 그룹에 홍보 메시지를 안전 게시하는 엔진
[방법 1] Ban 위험 0% — 강제 초대 없이 정보 제공형 메시지로 자연 홍보
[분리] K-Market (가구/나눔) vs EasyTax (세무/환급) 완전 독립 운영
[안전] 그룹당 최소 5일 재게시 간격 엄수 (SQLite 추적)
"""

import os
import json
import random
import sqlite3
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import BASE_DIR, DATA_DIR, KST, get_now_kst

logger = logging.getLogger("TelegramOutreachPoster")

TARGET_GROUPS_FILE = DATA_DIR / "telegram_target_groups.json"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛋️ K-Market 전용 홍보 메시지 (국가별 언어 완전 현지화)
# 핵심: 광고처럼 보이지 않는 "정보 제공형" 문체
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KMARKET_OUTREACH_MESSAGES = {
    "uz": (
        "🇰🇷 Koreyadagi do'stlar! 🛋️\n\n"
        "Xonaga ko'chib o'tyapsizmi? Mebelga pul sarflamang!\n\n"
        "K-Market Korea guruhida har kuni BEPUL mebel:\n"
        "🛏️ Yotoq + matras (0 won)\n"
        "❄️ Kichik muzlatgich / mikroto'lqinli pech (0 won)\n"
        "🪑 O'quv stoli + stul (0 won)\n\n"
        "📌 Guruhga kiring: {group_link}\n"
        "17 tilda real vaqt tarjimasi bor — koreyscha bilmasangiz ham muammo yo'q!"
    ),
    "vi": (
        "🇰🇷 Cộng đồng người Việt tại Hàn! 🛋️\n\n"
        "Đang dọn vào phòng mới? Đừng tốn tiền mua đồ nội thất!\n\n"
        "Nhóm K-Market Korea có đồ MIỄN PHÍ mỗi ngày:\n"
        "🛏️ Giường đơn + đệm (0 won)\n"
        "❄️ Tủ lạnh mini / lò vi sóng (0 won)\n"
        "🪑 Bàn học + ghế (0 won)\n\n"
        "📌 Tham gia nhóm: {group_link}\n"
        "Dịch tự động 17 ngôn ngữ — không cần biết tiếng Hàn!"
    ),
    "ru": (
        "🇰🇷 Привет всем в Корее! 🛋️\n\n"
        "Переезжаете? Не тратьте деньги на мебель!\n\n"
        "В группе K-Market Korea каждый день БЕСПЛАТНО:\n"
        "🛏️ Кровать + матрас (0 вон)\n"
        "❄️ Мини-холодильник / микроволновка (0 вон)\n"
        "🪑 Письменный стол + стул (0 вон)\n\n"
        "📌 Присоединяйтесь: {group_link}\n"
        "Автоперевод на 17 языков — корейский не нужен!"
    ),
    "mn": (
        "🇰🇷 Солонгост байгаа залуус аа! 🛋️\n\n"
        "Шинэ өрөөнд нүүж байна уу? Тавилгад мөнгө зарахгүй!\n\n"
        "K-Market Korea группт өдөр бүр ҮНЭГҮЙ:\n"
        "🛏️ Ор + матрас (0 вон)\n"
        "❄️ Жижиг хөргөгч / богино долгионы зуух (0 вон)\n"
        "🪑 Суралцах ширээ + сандал (0 вон)\n\n"
        "📌 Группт нэгдэх: {group_link}\n"
        "17 хэлний автомат орчуулга — солонгосоор мэдэхгүй ч асуудалгүй!"
    ),
    "en": (
        "🇰🇷 Expats in Korea! 🛋️\n\n"
        "Moving to a new room? Don't spend money on furniture!\n\n"
        "K-Market Korea Group has FREE items every day:\n"
        "🛏️ Single bed + mattress (0 won)\n"
        "❄️ Mini fridge / microwave (0 won)\n"
        "🪑 Study desk + chair (0 won)\n\n"
        "📌 Join here: {group_link}\n"
        "Auto-translation in 17 languages — no Korean needed!"
    ),
    "tl": (
        "🇰🇷 Mga Pinoy sa Korea! 🛋️\n\n"
        "Lilipat ng bagong kwarto? Huwag gumastos sa muwebles!\n\n"
        "Sa K-Market Korea Group may LIBRENG gamit araw-araw:\n"
        "🛏️ Kama + kutson (0 won)\n"
        "❄️ Mini-ref / microwave (0 won)\n"
        "🪑 Study table + upuan (0 won)\n\n"
        "📌 Sumali dito: {group_link}\n"
        "Auto-translate sa 17 wika — hindi kailangang marunong ng Korean!"
    ),
    "th": (
        "🇰🇷 ชาวไทยในเกาหลี! 🛋️\n\n"
        "กำลังย้ายห้องใหม่ไหม? ไม่ต้องเสียเงินซื้อเฟอร์นิเจอร์!\n\n"
        "กลุ่ม K-Market Korea มีของ ฟรี ทุกวัน:\n"
        "🛏️ เตียงเดี่ยว + ที่นอน (0 วอน)\n"
        "❄️ ตู้เย็นมินิ / ไมโครเวฟ (0 วอน)\n"
        "🪑 โต๊ะเรียน + เก้าอี้ (0 วอน)\n\n"
        "📌 เข้าร่วมกลุ่ม: {group_link}\n"
        "แปลอัตโนมัติ 17 ภาษา — ไม่ต้องรู้ภาษาเกาหลี!"
    ),
    "id": (
        "🇰🇷 Komunitas Indonesia di Korea! 🛋️\n\n"
        "Mau pindah kamar baru? Jangan habiskan uang untuk furnitur!\n\n"
        "Grup K-Market Korea ada barang GRATIS setiap hari:\n"
        "🛏️ Kasur + ranjang (0 won)\n"
        "❄️ Kulkas mini / microwave (0 won)\n"
        "🪑 Meja belajar + kursi (0 won)\n\n"
        "📌 Bergabung di sini: {group_link}\n"
        "Terjemahan otomatis 17 bahasa — tidak perlu bisa bahasa Korea!"
    ),
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💰 EasyTax 전용 홍보 메시지 (국가별 언어 완전 현지화)
# E-9/D-2 외국인 근로자/유학생 타깃 세무 정보 중심
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EASYTAX_OUTREACH_MESSAGES = {
    "uz": (
        "🇰🇷 Koreyadagi ishchilar uchun muhim ma'lumot! 💰\n\n"
        "Bilasizmi? Koreya hukumati sizga SOLIQ QAYTARISHI berishi mumkin!\n\n"
        "✅ Kichik korxonada ishlovchilar: 90% chegirma (30-modda,조특법)\n"
        "✅ Talabalar (D-2 viza): 3.3% soliq to'liq qaytariladi\n"
        "✅ O'tgan 5 yil uchun ham qaytarish mumkin!\n\n"
        "📌 Bepul tekshirish: {group_link}\n"
        "Oldindan to'lov yo'q — faqat qaytarilgandan keyin haq to'lanadi!"
    ),
    "vi": (
        "🇰🇷 Thông tin quan trọng cho người lao động tại Hàn! 💰\n\n"
        "Chính phủ Hàn Quốc có thể HOÀN THUẾ cho bạn!\n\n"
        "✅ Lao động SME: Giảm 90% thuế thu nhập (Điều 30, 조특법)\n"
        "✅ Du học sinh (D-2): Hoàn toàn bộ 3.3% bị khấu trừ\n"
        "✅ Có thể truy thu 5 năm qua!\n\n"
        "📌 Tra cứu miễn phí: {group_link}\n"
        "Không trả trước — chỉ thanh toán sau khi nhận được tiền!"
    ),
    "ru": (
        "🇰🇷 Важно для работающих в Корее! 💰\n\n"
        "Государство Кореи может вернуть вам НАЛОГИ!\n\n"
        "✅ Работники МСП: скидка 90% на подоходный налог (ст. 30)\n"
        "✅ Студенты (виза D-2): полный возврат удержанных 3,3%\n"
        "✅ Можно вернуть за последние 5 лет!\n\n"
        "📌 Бесплатная проверка: {group_link}\n"
        "Без предоплаты — платите только после получения возврата!"
    ),
    "mn": (
        "🇰🇷 Солонгост ажиллагсдад чухал мэдээлэл! 💰\n\n"
        "Солонгосын засгийн газар танд ТАТВАР БУЦААЖ өгч болно!\n\n"
        "✅ Жижиг дунд аж ахуйд ажиллагсад: 90% хөнгөлөлт (30 дугаар зүйл)\n"
        "✅ Оюутнууд (D-2 виз): 3.3% суутган татварыг бүрэн буцаана\n"
        "✅ Өнгөрсөн 5 жилийн татварыг буцааж авах боломжтой!\n\n"
        "📌 Үнэгүй шалгах: {group_link}\n"
        "Урьдчилгаа төлбөргүй — зөвхөн буцааж авсны дараа төлнө!"
    ),
    "en": (
        "🇰🇷 Important for Foreign Workers in Korea! 💰\n\n"
        "The Korean government can REFUND your taxes!\n\n"
        "✅ SME workers: 90% Income Tax Exemption (Article 30, Special Tax Act)\n"
        "✅ Students (D-2 visa): Full refund of withheld 3.3%\n"
        "✅ Can claim back up to 5 years!\n\n"
        "📌 Free check here: {group_link}\n"
        "No upfront fee — pay only AFTER you receive the refund!"
    ),
    "tl": (
        "🇰🇷 Mahalaga para sa mga manggagawa sa Korea! 💰\n\n"
        "Maaari kang makakuha ng TAX REFUND mula sa gobyerno ng Korea!\n\n"
        "✅ Manggagawa sa SME: 90% Tax Exemption (Article 30)\n"
        "✅ Estudyante (D-2 visa): Buong refund ng 3.3% na bawas\n"
        "✅ Maaaring mag-claim hanggang 5 taon!\n\n"
        "📌 Libreng tsek dito: {group_link}\n"
        "Walang bayad bago — bayad lang pagkatapos matanggap ang refund!"
    ),
    "th": (
        "🇰🇷 สำคัญสำหรับแรงงานต่างชาติในเกาหลี! 💰\n\n"
        "รัฐบาลเกาหลีสามารถคืนภาษีให้คุณได้!\n\n"
        "✅ พนักงาน SME: ลดหย่อนภาษีเงินได้ 90% (มาตรา 30)\n"
        "✅ นักศึกษา (วีซ่า D-2): คืนภาษีหัก 3.3% ทั้งหมด\n"
        "✅ สามารถย้อนหลังได้ถึง 5 ปี!\n\n"
        "📌 ตรวจสอบฟรีที่นี่: {group_link}\n"
        "ไม่มีค่าบริการล่วงหน้า — จ่ายหลังได้รับเงินคืนเท่านั้น!"
    ),
    "id": (
        "🇰🇷 Penting untuk pekerja asing di Korea! 💰\n\n"
        "Pemerintah Korea bisa MENGEMBALIKAN pajak Anda!\n\n"
        "✅ Pekerja UKM: Pengecualian pajak 90% (Pasal 30)\n"
        "✅ Mahasiswa (visa D-2): Pengembalian penuh 3.3% yang dipotong\n"
        "✅ Bisa klaim hingga 5 tahun ke belakang!\n\n"
        "📌 Cek gratis di sini: {group_link}\n"
        "Tidak ada biaya di muka — bayar hanya SETELAH menerima pengembalian!"
    ),
}


class TelegramOutreachPoster:
    """
    📢 타 텔레그램 공개 그룹 홍보 게시 엔진 (K-Market / EasyTax 완전 분리)
    - Ban 위험 0%: 강제 초대 없이 정보 제공형 메시지 게시
    - 그룹당 최소 5일 게시 간격 엄수 (SQLite 추적)
    - 언어별 현지화 메시지 자동 선택
    """

    MIN_POST_INTERVAL_DAYS = 5  # 그룹당 최소 재게시 간격(일)

    def __init__(
        self,
        brand: str = "kmarket",
        api_id: int = None,
        api_hash: str = None,
        session_name: str = None,
        db_path: Path = None
    ):
        self.brand = brand.lower()

        if self.brand == "easytax":
            self.api_id      = api_id   or int(os.getenv("EASYTAX_TELETHON_API_ID",  os.getenv("TELEGRAM_API_ID", "0")))
            self.api_hash    = api_hash or os.getenv("EASYTAX_TELETHON_API_HASH", os.getenv("TELEGRAM_API_HASH", ""))
            self.session_name = session_name or "easytax_outreach"
            self.group_link  = os.getenv("EASYTAX_TELEGRAM_GROUP_LINK", "https://t.me/easytax_korea_official")
        else:
            self.api_id      = api_id   or int(os.getenv("KMARKET_TELETHON_API_ID",  os.getenv("TELEGRAM_API_ID", "0")))
            self.api_hash    = api_hash or os.getenv("KMARKET_TELETHON_API_HASH", os.getenv("TELEGRAM_API_HASH", ""))
            self.session_name = session_name or "kmarket_outreach"
            self.group_link  = os.getenv("KMARKET_TELEGRAM_GROUP_LINK", "https://t.me/kmarket_korea_official")

        self.db_path = db_path or (DATA_DIR / "telegram_outreach_history.db")
        self._init_db()
        self._load_target_groups()

    # ─── DB 초기화 ──────────────────────────────────────────
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS outreach_posts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                brand        TEXT NOT NULL,
                group_username TEXT NOT NULL,
                lang         TEXT,
                msg_preview  TEXT,
                posted_at    TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS outreach_last (
                brand          TEXT NOT NULL,
                group_username TEXT NOT NULL,
                last_posted_at TIMESTAMP,
                total_posts    INTEGER DEFAULT 0,
                PRIMARY KEY (brand, group_username)
            )
        """)
        conn.commit()
        conn.close()

    def _load_target_groups(self):
        if TARGET_GROUPS_FILE.exists():
            with open(TARGET_GROUPS_FILE, "r", encoding="utf-8") as f:
                self.target_groups = json.load(f)
        else:
            self.target_groups = []

    # ─── 게시 가능 여부 판단 ─────────────────────────────────
    def can_post(self, group_username: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT last_posted_at FROM outreach_last WHERE brand=? AND group_username=?",
            (self.brand, group_username)
        )
        row = cur.fetchone()
        conn.close()
        if not row or not row[0]:
            return True
        last = datetime.datetime.fromisoformat(row[0])
        now  = get_now_kst()
        if last.tzinfo is None:
            last = last.replace(tzinfo=KST)
        return (now - last).total_seconds() / 86400 >= self.MIN_POST_INTERVAL_DAYS

    def _record_post(self, group_username: str, lang: str, msg: str):
        now_iso = get_now_kst().isoformat()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO outreach_posts (brand, group_username, lang, msg_preview, posted_at) VALUES (?,?,?,?,?)",
            (self.brand, group_username, lang, msg[:120], now_iso)
        )
        cur.execute("""
            INSERT INTO outreach_last (brand, group_username, last_posted_at, total_posts) VALUES (?,?,?,1)
            ON CONFLICT(brand, group_username)
            DO UPDATE SET last_posted_at=excluded.last_posted_at, total_posts=total_posts+1
        """, (self.brand, group_username, now_iso))
        conn.commit()
        conn.close()

    # ─── 메시지 생성 ─────────────────────────────────────────
    def build_message(self, group_lang: str) -> str:
        templates = EASYTAX_OUTREACH_MESSAGES if self.brand == "easytax" else KMARKET_OUTREACH_MESSAGES
        template  = templates.get(group_lang) or templates.get("en", "")
        return template.format(group_link=self.group_link)

    # ─── 다음 타깃 그룹 선정 ─────────────────────────────────
    def _get_next_group(self):
        active   = [g for g in self.target_groups if g.get("is_active", True)]
        eligible = [g for g in active if self.can_post(g.get("username", ""))]
        if not eligible:
            return None
        eligible.sort(key=lambda x: (-x.get("priority_score", 0), x.get("last_posted_at") or ""))
        return eligible[0]

    # ─── 1회 아웃리치 사이클 ─────────────────────────────────
    def execute_outreach_cycle(self) -> Dict[str, Any]:
        active   = [g for g in self.target_groups if g.get("is_active", True)]
        eligible = [g for g in active if self.can_post(g.get("username", ""))]
        if not eligible:
            return {
                "success": True,
                "status": "NO_ELIGIBLE_GROUPS",
                "brand": self.brand,
                "message": f"[{self.brand}] 게시 가능한 그룹 없음 ({self.MIN_POST_INTERVAL_DAYS}일 간격 유지 중)"
            }

        eligible.sort(key=lambda x: (-x.get("priority_score", 0), x.get("last_posted_at") or ""))

        last_error = None
        for target in eligible:
            username = target.get("username", "")
            lang     = target.get("language", "en")
            name     = target.get("name", username)
            msg      = self.build_message(lang)

            ok, err_msg = self._perform_post(username, msg)
            if ok:
                self._record_post(username, lang, msg)
                logger.info(f"✅ [{self.brand.upper()}] 아웃리치 게시 완료: '{name}' (@{username})")
                return {
                    "success": True, "status": "POSTED", "brand": self.brand,
                    "group_name": name, "group_username": username, "lang": lang,
                    "message_preview": msg[:80] + "..."
                }
            else:
                last_error = f"@{username}: {err_msg}"
                logger.warning(f"⚠️ [{self.brand.upper()}] @{username} 게시 제한 -> 다음 그룹 진행 ({err_msg})")
                # 쿨다운 기록하여 제한된 방에 계속 재시도하지 않도록 방지
                self._record_post(username, lang, f"[RESTRICTED] {err_msg}")
                continue

        return {
            "success": False, "status": "POST_FAILED", "brand": self.brand,
            "error": f"모든 대상 그룹 게시 제한 ({last_error})"
        }

    # ─── 실제 Telethon 게시 ──────────────────────────────────
    def _perform_post(self, group_username: str, message: str) -> (bool, str):
        session_path = BASE_DIR / f"{self.session_name}.session"
        if not session_path.exists():
            err = f"세션 파일 없음: '{self.session_name}.session'"
            logger.warning(f"⚠️  [{self.brand.upper()}] {err}")
            return False, err
        try:
            from telethon.sync import TelegramClient
            from telethon.tl.functions.channels import JoinChannelRequest
            with TelegramClient(str(BASE_DIR / self.session_name), self.api_id, self.api_hash) as client:
                try:
                    client(JoinChannelRequest(group_username))
                except Exception:
                    pass
                client.send_message(group_username, message)
            return True, "OK"
        except Exception as e:
            logger.error(f"❌ [{self.brand.upper()}] Telethon 게시 오류 (@{group_username}): {e}")
            return False, str(e)

    # ─── 대시보드 통계 ───────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM outreach_posts WHERE brand=?", (self.brand,))
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT group_username, last_posted_at, total_posts FROM outreach_last WHERE brand=? ORDER BY last_posted_at DESC LIMIT 5",
            (self.brand,)
        )
        recent = [{"group": r[0], "last_posted": r[1], "total": r[2]} for r in cur.fetchall()]
        conn.close()
        eligible = sum(1 for g in self.target_groups if g.get("is_active", True) and self.can_post(g.get("username", "")))
        return {
            "brand": self.brand,
            "total_posts": total,
            "eligible_groups_now": eligible,
            "target_groups_total": len([g for g in self.target_groups if g.get("is_active", True)]),
            "min_interval_days": self.MIN_POST_INTERVAL_DAYS,
            "session_ready": (BASE_DIR / f"{self.session_name}.session").exists(),
            "recent_posts": recent
        }
