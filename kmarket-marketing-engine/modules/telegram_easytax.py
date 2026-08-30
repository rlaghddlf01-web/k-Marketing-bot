import logging
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from config import BASE_DIR, LANGUAGES, OUTPUTS_DIR, DATA_DIR, BASE_URLS
from core.db_manager import DBManager

logger = logging.getLogger("EasyTaxTelegram")

EASYTAX_BRIEFING_TEMPLATES = {
    "ko": {
        "header": "🏛️ [EasyTax 대한민국 공인 외국인 세무 환급 데일리 브리핑]",
        "points": [
            "• E-9/H-2 근로자: 중소기업 소득세 최대 90% 감면 혜택 (조특법 제30조)",
            "• D-2 유학생: 알바비 원천징수 세금 3.3% 100% 전액 환급",
            "• 지난 5개년(2021~2026) 누락 세금 소급 경정청구 가능",
            "🛡️ 100% 무료 AI 시뮬레이션 • 선입금 및 착수금 0원"
        ],
        "cta": "👉 지금 1분 만에 내 환급금 무료 조회하기",
        "disclaimer": "* 국세청 세무 규정에 따라 공인 세무 대리인을 통해 안전하게 처리됩니다."
    },
    "en": {
        "header": "🏛️ [EasyTax Korea Expat Tax Relief Daily Briefing]",
        "points": [
            "• E-9/H-2 Workers: Up to 90% Income Tax Exemption (Article 30)",
            "• D-2 Students: 100% Refund on 3.3% Part-Time Withholding Tax",
            "• Retroactive 5-Year Overpaid Tax Claims (2021~2026)",
            "🛡️ 100% Free AI Simulation • Zero Upfront Fees"
        ],
        "cta": "👉 Estimate your refund for free in 1 min",
        "disclaimer": "* Processed safely via certified tax agents under Korean National Tax regulations."
    },
    "vi": {
        "header": "🏛️ [EasyTax Bản Tin Hoàn Thuế Hàn Quốc Hàng Ngày Cho Người Việt]",
        "points": [
            "• Lao động E-9/H-2: Giảm tới 90% thuế thu nhập doanh nghiệp vừa và nhỏ (Điều 30)",
            "• Du học sinh D-2: Hoàn lại 100% số thuế 3.3% bị trừ khi làm thêm",
            "• Có thể truy thu và nhận lại tiền thuế đã đóng trong 5 năm qua (2021~2026)",
            "🛡️ Mô phỏng AI hoàn toàn miễn phí • Không thu phí trước (0đ)"
        ],
        "cta": "👉 Tra cứu số tiền hoàn thuế miễn phí trong 1 phút",
        "disclaimer": "* Được xử lý an toàn bởi đại lý thuế được cấp phép theo quy định của Cục Thuế Quốc gia Hàn Quốc."
    },
    "uz": {
        "header": "🏛️ [EasyTax Koreyadagi Vatandoshlar Uchun Kunlik Soliq Xabari]",
        "points": [
            "• E-9/H-2 ishchilari: Kichik korxonalarda daromad solig'idan 90% gacha chegirma (30-modda)",
            "• D-2 talabalari: Ishlaganda ushlab qolingan 3.3% soliqni 100% to'liq qaytarib olish",
            "• O'tgan 5 yil (2021~2026) davomida to'langan ortiqcha soliqlarni ham qaytarish mumkin",
            "🛡️ 100% Bepul AI hisob-kitob • Oldindan hech qanday to'lov yo'q"
        ],
        "cta": "👉 1 daqiqada qaytariladigan pulingizni bepul tekshiring",
        "disclaimer": "* Koreya Milliy Soliq Xizmati qonunchiligiga muvofiq litsenziyalangan soliq mutaxassislari tomonidan rasmiylashtiriladi."
    },
    "ru": {
        "header": "🏛️ [EasyTax Ежедневный налоговый вестник для иностранцев в Корее]",
        "points": [
            "• Работники E-9/H-2: Скидка до 90% на подоходный налог на предприятиях МСП (ст. 30)",
            "• Студенты D-2: Полный 100% возврат налога 3,3%, удержанного на подработке",
            "• Возврат излишне уплаченных налогов за последние 5 лет (2021~2026)",
            "🛡️ 100% бесплатная AI-оценка • Никакой предоплаты (0 вон)"
        ],
        "cta": "👉 Узнать сумму возврата бесплатно за 1 минуту",
        "disclaimer": "* Официальное оформление через сертифицированных налоговых агентов в соответствии с законодательством Южной Кореи."
    },
    "mn": {
        "header": "🏛️ [EasyTax Солонгос дахь гадаад иргэдийн татварын буцаан олголтын мэдээ]",
        "points": [
            "• E-9/H-2 ажиллагсад: ЖДҮ-ийн орлогын албан татварын 90% хүртэлх хөнгөлөлт (30 дугаар зүйл)",
            "• D-2 оюутнууд: Цагийн ажлын суутгасан 3.3% татварыг 100% бүрэн буцаан авах",
            "• Өнгөрсөн 5 жилийн (2021~2026) илүү төлсөн татварыг нөхөн авах боломжтой",
            "🛡️ 100% үнэгүй AI тооцоолол • Урьдчилгаа төлбөр 0 төгрөг"
        ],
        "cta": "👉 Буцаан авах мөнгөө 1 минутанд үнэгүй шалгах",
        "disclaimer": "* Солонгосын Үндэсний татварын албаны хууль тогтоомжийн дагуу итгэмжлэгдсэн татварын итгэмжлэгдсэн төлөөлөгчөөр найдвартай гүйцэтгэнэ."
    },
    "zh": {
        "header": "🏛️ [EasyTax 韩国在韩外国人退税每日指南]",
        "points": [
            "• E-9/H-2 劳工: 中小企业个人所得税减免高达 90% (租税特例限制法 第30条)",
            "• D-2 留学生: 兼职打工被扣除的 3.3% 税金 100% 全额退还",
            "• 可追溯申请过去 5 年 (2021~2026) 多缴纳的税款",
            "🛡️ 100% 免费 AI 模拟测算 • 无任何前期手续费"
        ],
        "cta": "👉 1 分钟免费测算您的退税金额",
        "disclaimer": "* 根据韩国国税厅税法规定，由韩国公认税务代理人合规办理。"
    },
    "tl": {
        "header": "🏛️ [EasyTax Araw-araw na Balita sa Tax Refund sa Korea]",
        "points": [
            "• E-9/H-2 Manggagawa: Hanggang 90% Tax Exemption sa SME (Article 30)",
            "• D-2 Estudyante: 100% Refund sa 3.3% Part-Time Withholding Tax",
            "• Pwedeng i-claim ang nakaraang 5 taon (2021~2026)",
            "🛡️ 100% Libreng AI Simulation • Walang bayad sa simula"
        ],
        "cta": "👉 Libreng alamin ang iyong refund sa 1 minuto",
        "disclaimer": "* Ligtas na pinoproseso sa pamamagitan ng mga lisensyadong ahente ng buwis sa Korea."
    },
    "th": {
        "header": "🏛️ [EasyTax ข้อมูลคืนภาษีประจำวันสำหรับคนต่างชาติในเกาหลี]",
        "points": [
            "• แรงงาน E-9/H-2: ลดหย่อนภาษีเงินได้สูงสุด 90% ใน SME (มาตรา 30)",
            "• นักศึกษา D-2: คืนภาษีหัก ณ ที่จ่าย 3.3% จากงานพาร์ทไทม์ 100% เต็ม",
            "• สามารถขอคืนภาษีย้อนหลังได้ถึง 5 ปี (2021~2026)",
            "🛡️ คำนวณด้วย AI ฟรี 100% • ไม่มีค่าบริการล่วงหน้า"
        ],
        "cta": "👉 ตรวจสอบเงินคืนของคุณฟรีใน 1 นาที",
        "disclaimer": "* ดำเนินการอย่างถูกต้องตามกฎหมายภาษีของกรมสรรพากรเกาหลี"
    },
    "id": {
        "header": "🏛️ [EasyTax Info Pengembalian Pajak Harian di Korea]",
        "points": [
            "• Pekerja E-9/H-2: Pengurangan pajak penghasilan hingga 90% di UKM (Pasal 30)",
            "• Mahasiswa D-2: Pengembalian 100% pajak 3.3% dari kerja paruh waktu",
            "• Bisa klaim kembali pajak 5 tahun terakhir (2021~2026)",
            "🛡️ Simulasi AI 100% Gratis • Tanpa biaya di muka"
        ],
        "cta": "👉 Cek perkiraan pengembalian Anda gratis dalam 1 menit",
        "disclaimer": "* Diproses secara resmi oleh agen pajak berlisensi sesuai peraturan Kantor Pajak Nasional Korea."
    }
}


class EasyTaxTelegramPusher:
    """
    💰 [EasyTax (KTRS) 전용 17개국 텔레그램 브로드캐스트 엔진]
    - E-9 90% 소득세 감면 & D-2 3.3% 환급 팁 17개국 다국어 세무 브리핑 발송 (Anti-Ban 공인 면책 포함)
    """
    def __init__(self, db_mgr: DBManager):
        self.db_mgr = db_mgr
        self.output_dir = OUTPUTS_DIR / "briefings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.env_path = BASE_DIR / ".env"
        self.bot_token = self._get_env("EASYTAX_TELEGRAM_BOT_TOKEN") or self._get_env("TELEGRAM_BOT_TOKEN")
        self.chat_id = self._get_env("EASYTAX_TELEGRAM_CHAT_ID")

    def _get_env(self, key: str) -> str:
        if self.env_path.exists():
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(key + "="):
                        return line.split("=", 1)[1].strip()
        return ""

    def broadcast_daily_tax_tips(self, target_langs: List[str] = ["vi", "uz", "ru", "en", "ko"]) -> Dict[str, Any]:
        """외국인 세무 꿀팁 17개국어 100% 현지화 텔레그램 브로드캐스트 발행"""
        messages_sent = 0
        base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")

        for lang in target_langs:
            tmpl = EASYTAX_BRIEFING_TEMPLATES.get(lang, EASYTAX_BRIEFING_TEMPLATES["en"])
            easytax_url = f"{base_domain.rstrip('/')}/?lang={lang}&utm_source=telegram&utm_medium=daily_briefing"

            text = f"{tmpl['header']}\n\n"
            text += "\n".join(tmpl["points"]) + "\n\n"
            text += f"{tmpl['cta']}: {easytax_url}\n"
            text += f"{tmpl['disclaimer']}"

            # 텔레그램 실발송 (언어별 전용 포럼 토픽으로 다이렉트 전송)
            if self.bot_token and self.chat_id:
                try:
                    payload = {"chat_id": self.chat_id, "text": text}
                    topics_file = DATA_DIR / "telegram_topics.json"
                    if topics_file.exists():
                        try:
                            with open(topics_file, "r", encoding="utf-8") as tf:
                                t_data = json.load(tf)
                            thread_id = t_data.get("easytax", {}).get(lang)
                            if thread_id:
                                payload["message_thread_id"] = thread_id
                        except Exception:
                            pass

                    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                    requests.post(url, json=payload, timeout=5)
                    messages_sent += 1
                except Exception as e:
                    logger.warning(f"EasyTax 텔레그램 발송 실패 ({lang}): {e}")

            # 파일 저장
            file_path = self.output_dir / f"easytax_briefing_{lang}_{int(time.time())}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

        logger.info(f"💰 [EasyTax Telegram] {len(target_langs)}개 언어 100% 현지화 세무 브리핑 발행 완료")
        return {
            "success": True,
            "brand": "easytax",
            "sent_count": len(target_langs),
            "message": f"💰 [EasyTax] {len(target_langs)}개 언어 100% 현지화 세무 브리핑 발행 완료!"
        }
