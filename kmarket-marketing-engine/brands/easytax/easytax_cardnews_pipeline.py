# -*- coding: utf-8 -*-
"""
EasyTaxCardNewsPipeline - 📸 [이지택스 전용 1080x1350 온전한 풀사이즈 카드뉴스 생산 공장]
- 7:3 분할 박스 전면 폐기 -> 100% 1080x1350 풀블리드(Full-Bleed) 고화질 사진 배치
- 하단 35% 영역에 부드러운 그라디언트 스크림(Gradient Scrim)으로 텍스트 가독성 극대화
- 좌측 여백(x=85~120px) 공중에 3D 드롭 섀도우를 머금은 스마트폰 플로팅 인셋 (얼굴 가림 0%, 손가락 기괴함 0%)
- 골드 헤드라인 + 세무사 공식 뱃지 + CTA 버튼 잡지 표지 스타일 오버레이
- 4대 SNS(스레드, 인스타, 페북, 텔레그램) 검색최적화(SEO) 포스팅 가이드 동시 출력
- 로컬 바탕화면 전용 출력
"""

import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from core.screen_inset_compositor import ScreenInsetCompositor
from .ui_templates.refund_receipt_template import RefundReceiptTemplate
from .scenarios.prompt_director_cardnews import PromptDirectorCardNewsEasyTax
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter

logger = logging.getLogger("EasyTaxCardNewsPipeline")


class EasyTaxCardNewsPipeline:
    """이지택스 1080x1350 온전한 풀사이즈 카드뉴스 자동 생산 파이프라인"""

    def __init__(self):
        self.embedder = PhoneScreenEmbedder()
        self.inset_compositor = ScreenInsetCompositor()
        self.ui_template = RefundReceiptTemplate()
        self.copywriter = GeminiCardnewsCopywriter(service_id="easytax")
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")

    def produce(
        self,
        nationality_code: str = "vi",
        amount: int = 3100000,
        custom_master_image: Image.Image = None,
        use_floating_phone: bool = True,
        output_filename: str = "easytax_cardnews_master.png"
    ) -> str:
        """이지택스 1080x1350 온전한 풀사이즈 카드뉴스 1회 완성 실행"""
        # 1. 영수증 UI 생성 (동적 금액)
        ui_img = self.ui_template.render(amount=amount)

        # 2. 마스터 베이스 사진 로드
        if custom_master_image is not None:
            master_img = custom_master_image
        else:
            default_candidate = self.desktop / "vietnamese_deep_focus_presenter.png"
            if default_candidate.exists():
                master_img = Image.open(str(default_candidate))
            else:
                # 대체 사진
                master_img = Image.open(str(self.desktop / "vietnamese_refund_completed.png"))

        # 3. 스마트폰 화면 합성 (대표님 지침: 좌측 3D 플로팅 또는 정밀 매립)
        if use_floating_phone:
            # [대표님 선택 해결책 2] 인물 얼굴 가림 0%, 손가락 기괴함 0%:
            # 인물 반대편(좌측 여백) 공중에 3D 드롭 섀도우를 머금고 둥둥 뜬 스마트폰 합성
            embedded_img = self.inset_compositor.composite_custom_ui_onto_photo(
                base_photo=master_img,
                ui_image=ui_img,
                position="left_floating",
                scale=0.58
            )
        else:
            # OpenCV 정밀 액정 매립
            embedded_img = self.embedder.embed_screen(base_image=master_img, ui_image=ui_img)

        # 4. [7:3 분할 폐기] 1080x1350 온전한 풀사이즈 캔버스 합성
        canvas = Image.new("RGB", (1080, 1350), (11, 19, 43))

        # 사진 1080x1350 풀블리드(Full-Bleed) 센터 크롭 리사이즈
        W, H = embedded_img.size
        scale = max(1080 / W, 1350 / H)
        resized_photo = embedded_img.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)

        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 1350) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1350))
        canvas.paste(photo_cropped, (0, 0))

        # 5. 하단 부드러운 그라디언트 스크림 (Gradient Scrim) 오버레이
        # y=820부터 y=1350까지 자연스럽게 짙어지는 암영 레이어
        gradient_layer = Image.new("RGBA", (1080, 1350), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(gradient_layer)
        scrim_start_y = 800
        scrim_height = 1350 - scrim_start_y

        for i in range(scrim_height):
            curr_y = scrim_start_y + i
            ratio = i / float(scrim_height)
            # 3차 가속 부드러운 감쇠 곡선 (Cubic Ease-In)
            alpha = int((ratio ** 2.2) * 238)
            g_draw.line([(0, curr_y), (1080, curr_y)], fill=(11, 19, 43, alpha))

        canvas = Image.alpha_composite(canvas.convert("RGBA"), gradient_layer).convert("RGB")
        draw = ImageDraw.Draw(canvas)

        # 6. 세련된 매거진 타이포그래피 (골드 헤드라인 + 플로팅 뱃지 + CTA)
        copy = PromptDirectorCardNewsEasyTax.get_copywriting(nationality_code, amount=amount)

        font_head = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 44)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 25)
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)

        # 플로팅 뱃지 (상단 왼쪽, y=910)
        badge_box = [(60, 910), (350, 952)]
        draw.rounded_rectangle(badge_box, radius=8, fill=(30, 80, 160))
        draw.text((75, 918), copy["badge"], fill=(255, 255, 255), font=font_badge)

        # 골드 헤드라인 (y=970)
        draw.text((60, 970), copy["headline"], fill=(255, 215, 0), font=font_head)

        # 서브카피 (y=1045)
        draw.text((60, 1045), copy["subhead"], fill=(225, 230, 240), font=font_sub)

        # CTA 버튼 (하단 중앙, y=1180~1270)
        draw.rounded_rectangle([(60, 1180), (1020, 1270)], radius=18, fill=(212, 175, 55))
        bbox_cta = draw.textbbox((0, 0), copy["cta"], font=font_head)
        tw_cta = bbox_cta[2] - bbox_cta[0]
        draw.text(((1080 - tw_cta) // 2, 1198), copy["cta"], fill=(15, 23, 42), font=font_head)

        # 7. 이미지 로컬 바탕화면 전용 저장
        out_desktop = self.desktop / output_filename
        canvas.save(str(out_desktop), "PNG", quality=95)

        # 8. [대표님 지침] 4대 SNS(스레드, 인스타, 페북, 텔레그램) 배포 패키지 가이드 텍스트 자동 생성
        guide_filename = output_filename.replace(".png", "_SNS_가이드.txt")
        guide_path = self.desktop / guide_filename
        self._write_sns_posting_guide(
            file_path=guide_path,
            nationality_code=nationality_code,
            amount=amount,
            copy=copy
        )

        logger.info(f"🎉 [EasyTax 풀사이즈 카드뉴스] 완성! -> {out_desktop.name}")
        return str(out_desktop)

    def _write_sns_posting_guide(self, file_path: Path, nationality_code: str, amount: int, copy: dict):
        """스레드, 인스타그램, 페이스북, 텔레그램 4대 채널별 포스팅 가이드 텍스트 저장"""
        amount_fmt = f"{amount:,} KRW"
        
        content = f"""================================================================================
📢 [EasyTax 카드뉴스 공식 SNS 포스팅 패키지] ({nationality_code.upper()} / {amount_fmt})
================================================================================

1. 🧵 스레드 (Threads) 포스팅 팩
--------------------------------------------------------------------------------
[헤드라인 텍스트]:
{copy.get('headline', '')} 🔥
한국에서 일하는 외국인 친구들, 작년에 낸 세금 얼마 돌려받았어?

[본문]:
국세청 조세특례제한법 30조로 {amount_fmt} 입금 완료된 실제 후기!
신청 안 하면 5년 지나고 국고로 환수돼서 영영 사라진대 😱
착수금 0원이고 국세청에서 돈 먼저 들어온 다음에 정산하는 거라 사기 걱정 0%임.

다들 프로필 링크에서 1분 만에 무료 조회해봐! 댓글로 얼마 나왔는지 공유하자 👇

[해시태그]:
#이지택스 #외국인근로자 #세금환급 #연말정산 #E9비자 #한국생활


2. 📸 인스타그램 (Instagram) 포스팅 팩
--------------------------------------------------------------------------------
[본문 캡션]:
🇰🇷 {copy.get('badge', '국세청 공식 세무 환급')}
"한국에서 열심히 땀 흘린 당신, {amount_fmt} 당연히 찾아가세요!"

많은 분들이 몰라서 놓치는 '외국인 근로자 90% 소득세 감면 혜택'
신청만 하면 5년 치 묵혀둔 세금이 내 통장으로 쏙 들어옵니다 💸

✨ 이지택스(EasyTax) 3대 안심 보증:
1️⃣ 착수금/선결제 0원! (환급금 먼저 입금 후 정산)
2️⃣ 공인 세무법인의 100% 합법 국세청 다이렉트 전산 처리
3️⃣ 스마트폰으로 단 1분 만에 모의 계산 완료!

지금 프로필 링크(Link in Bio)를 누르고 숨은 내 돈을 확인하세요! 🔍

[SEO 바이럴 해시태그]:
#EasyTax #HoànThuế #ThuếThuNhập #E9Visa #LaoĐộngHànQuốc #CuộcSốngHànQuốc #ViệtNamTạiHàn #이지택스 #외국인세금환급 #조특법30조 #국세청환급 #E9근로자 #E7비자 #유학생환급 #소득세감면 #환급금조회


3. 📘 페이스북 (Facebook) 커뮤니티 그룹 포스팅 팩
--------------------------------------------------------------------------------
[제목]:
{copy.get('headline', '')} - 외국인 근로자 필수 확인 정보!

[본문]:
한국에서 제조업, 농축산, 물류 현장에서 일하시는 외국인 여러분 안녕하십니까.
최근 5년 동안 대한민국 국세청에 납부하신 소득세 중 최대 90%를 돌려받으실 수 있습니다.

📌 핵심 안내:
- 조세특례제한법 제30조에 따른 합법적 세액 감면 청구
- 평균 환급액: 250만 ~ 450만 원 상당 ({amount_fmt} 수령 사례 다수)
- 선결제 수수료 일체 없음 (국세청 입금 완료 후 후불 정산)

신청 기한이 지나면 소멸되오니 아래 공식 웹사이트에서 지금 즉시 무료 조회를 진행해보시기 바랍니다.

👉 공식 간편 환급 조회: https://ktrs-service.vercel.app/?lang={nationality_code}


4. ✈️ 텔레그램 (Telegram) 단톡방 / 채널 팩
--------------------------------------------------------------------------------
⚡ [긴급 공지] 대한민국 국세청 외국인 소득세 환급 신청 안내

💰 환급 금액: {amount_fmt} 입금 완료
✅ 대상: 대한민국 체류 E-9, E-7, H-2, D-2 등 외국인 근로자
🛡️ 수수료: 0원 (100% 성과 후불제, 사전 비용 없음)

⏱️ 소요 시간: 1분 간편 조회
🔗 지금 확인하기: https://ktrs-service.vercel.app/?lang={nationality_code}
================================================================================
"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.warning(f"SNS 포스팅 가이드 작성 실패: {e}")

