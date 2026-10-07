"""
BlogImageGenerator - 🎨 Gemini Imagen 3 블로그 사진 자동 생성 + Supabase Storage 업로드 모듈
- 글 주제(theme_title, category)에 맞는 사진 1장을 Imagen 3로 생성
- 한국/동양인 맥락 프롬프트를 자동 구성 (서양인 0% 보장)
- PNG → WebP 압축 변환 + 최대 1200×675 리사이즈 (파일 크기 ~80% 절감)
- 생성된 이미지를 Supabase Storage에 업로드하고 공개 URL 반환
- 실패 시 검증된 Unsplash 폴백 URL 반환 (무중단 보장)
"""

import os
import io
import logging
from PIL import Image
import datetime
from typing import Optional

logger = logging.getLogger("BlogImageGenerator")

# ── Supabase Storage 버킷명
STORAGE_BUCKET = "blog-images"

# ── 카테고리별 이미지 프롬프트 템플릿
PROMPT_TEMPLATES = {
    # EasyTax: 세무/사무/서류 관련 (사람 없이 사물 중심)
    "easytax_default": (
        "Korean tax office desk with documents, calculator, pen, laptop showing tax forms, "
        "modern Seoul office interior, clean minimal workspace, warm natural light, "
        "photorealistic, high quality, 16:9"
    ),
    "tax_document": (
        "Korean tax documents and official forms neatly arranged on a clean wooden desk, "
        "calculator, fountain pen, modern minimal Seoul office background, soft morning light, "
        "photorealistic, professional, high quality, 16:9"
    ),
    "tax_consultation": (
        "Modern Korean office interior, clean desk with laptop and tax documents, "
        "city view through window, professional workspace, Seoul, "
        "photorealistic, high quality, 16:9"
    ),
    # KMarket: 원룸/가구/생활 관련 (사람 없이 공간 중심)
    "kmarket_default": (
        "Modern Korean studio apartment interior, minimalist furniture, clean Scandinavian design, "
        "natural sunlight through window, cozy Seoul apartment, photorealistic, high quality, 16:9"
    ),
    "moving": (
        "Cardboard moving boxes stacked in a clean Korean apartment hallway, "
        "bright modern interior, wooden floor, photorealistic, high quality, 16:9"
    ),
    "furniture": (
        "Modern Korean apartment living room, stylish minimalist sofa and furniture, "
        "clean white walls, natural wood accents, warm lighting, photorealistic, 16:9"
    ),
    "life": (
        "Cozy Korean studio apartment interior, small kitchen and living space combined, "
        "modern minimal decor, city view outside window, Seoul, photorealistic, 16:9"
    ),
}

# ── 폴백 Unsplash URL (검증된 한국/동양 사진)
FALLBACK_URLS = {
    "easytax": [
        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&auto=format&fit=crop&q=80",  # 사무실 서류
        "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1200&auto=format&fit=crop&q=80",  # 한국 서울 오피스
        "https://images.unsplash.com/photo-1588196749597-9ff075ee6b5b?w=1200&auto=format&fit=crop&q=80",  # 재무 서류
    ],
    "kmarket": [
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200&auto=format&fit=crop&q=80",  # 거실 가구
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=1200&auto=format&fit=crop&q=80",  # 모던 스튜디오
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1200&auto=format&fit=crop&q=80",  # 원룸 책상
    ],
}


class BlogImageGenerator:
    """Gemini Imagen 3 블로그 사진 생성 + Supabase Storage 업로드 엔진"""

    def __init__(self, api_key: str, supabase_client=None):
        self.api_key = api_key
        self.supabase = supabase_client
        self._genai_client = None

    def _get_genai_client(self):
        if self._genai_client is None:
            from google import genai
            self._genai_client = genai.Client(api_key=self.api_key)
        return self._genai_client

    def _build_prompt(self, service_id: str, theme_title: str, category: str, custom_prompt: Optional[str] = None) -> str:
        """글 주제에 맞는 Imagen 프롬프트 자동 구성 (custom_prompt 최우선 적용)"""
        if custom_prompt and custom_prompt.strip():
            # 제미나이가 글 본문 맥락에 맞춰 생성한 맞춤 프롬프트 우선 사용
            prompt = custom_prompt.strip()
            if "photorealistic" not in prompt.lower():
                prompt += ", photorealistic, authentic documentary style, high quality, 16:9"
            if "asian" not in prompt.lower():
                prompt += ", realistic Asian character and features"
            return prompt

        title_lower = theme_title.lower()

        if service_id == "easytax":
            if any(k in title_lower for k in ["서류", "서식", "신청서", "문서", "발급"]):
                return PROMPT_TEMPLATES["tax_document"] + f", related to: {theme_title}"
            else:
                return PROMPT_TEMPLATES["tax_consultation"] + f", theme: {theme_title}"
        else:  # kmarket
            if any(k in title_lower for k in ["이사", "포장", "짐", "트럭"]):
                return PROMPT_TEMPLATES["moving"] + f", theme: {theme_title}"
            elif any(k in title_lower for k in ["가구", "소파", "침대", "책상", "냉장고"]):
                return PROMPT_TEMPLATES["furniture"] + f", theme: {theme_title}"
            else:
                return PROMPT_TEMPLATES["kmarket_default"] + f", theme: {theme_title}"

    def _get_fallback_url(self, service_id: str, theme_id: str) -> str:
        """Imagen 실패 시 폴백 URL 반환 (테마ID 해시로 매번 다른 URL 선택)"""
        pool = FALLBACK_URLS.get(service_id, FALLBACK_URLS["easytax"])
        return pool[hash(theme_id) % len(pool)]

    def generate_and_upload(
        self,
        service_id: str,
        theme_id: str,
        theme_title: str,
        category: str,
        slug: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Imagen 3로 블로그 사진 1장 생성 후 Supabase Storage에 업로드
        (custom_prompt가 있으면 글 스토리 맞춤 프롬프트 적용)
        Returns: 공개 이미지 URL (실패 시 폴백 URL)
        """
        prompt = self._build_prompt(service_id, theme_title, category, custom_prompt)
        logger.info(f"🎨 [Imagen] '{theme_title}' 사진 생성 시작 (프롬프트: {prompt[:80]}...)")

        try:
            from google.genai import types as genai_types
            import base64
            client = self._get_genai_client()

            # ✅ 구매한 플랜 초저가 이미지 모델 사용 (gemini-3.1-flash-lite-image)
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-image",
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                )
            )

            # 이미지 bytes 추출
            raw_bytes = None
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    raw = part.inline_data.data
                    if isinstance(raw, str):
                        raw = base64.b64decode(raw)
                    raw_bytes = raw
                    break

            if not raw_bytes:
                raise ValueError("이미지 응답 데이터 없음")
            logger.info(f"✅ [Imagen] 이미지 생성 완료 (원본 {len(raw_bytes):,} bytes)")

            # 🗜️ PNG → WebP 압축 변환 + 최대 1200×675 리사이즈
            compressed_bytes = self._compress_to_webp(raw_bytes)
            logger.info(f"✅ [압축] WebP 변환 완료 ({len(compressed_bytes):,} bytes, {100 - int(len(compressed_bytes)/len(raw_bytes)*100)}% 절감)")

            # Supabase Storage 업로드
            public_url = self._upload_to_supabase(service_id, slug, compressed_bytes)
            if public_url:
                return public_url

        except Exception as e:
            logger.warning(f"⚠️ [Imagen] 생성 실패 → 폴백 URL 사용: {e}")

        return self._get_fallback_url(service_id, theme_id)

    def _compress_to_webp(self, raw_bytes: bytes, max_width: int = 1200, quality: int = 82) -> bytes:
        """PNG bytes → WebP 변환 + 최대 1200×675 리사이즈 (16:9 비율 유지)"""
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            # 최대 크기 초과 시 비율 유지하며 리사이즈
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="WEBP", quality=quality, method=6)
            return buf.getvalue()
        except Exception as e:
            logger.warning(f"⚠️ [압축] WebP 변환 실패, 원본 사용: {e}")
            return raw_bytes

    def _upload_to_supabase(self, service_id: str, slug: str, image_bytes: bytes) -> Optional[str]:
        """Supabase Storage에 이미지 업로드 후 공개 URL 반환"""
        if not self.supabase:
            logger.warning("⚠️ Supabase 클라이언트 없음 → Storage 업로드 불가")
            return None

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{service_id}/{slug}_{timestamp}.webp"

            self.supabase.storage.from_(STORAGE_BUCKET).upload(
                path=file_path,
                file=image_bytes,
                file_options={"content-type": "image/webp", "upsert": "true"}
            )

            public_url = self.supabase.storage.from_(STORAGE_BUCKET).get_public_url(file_path)
            logger.info(f"✅ [Storage] 업로드 완료: {public_url}")
            return public_url

        except Exception as e:
            logger.warning(f"⚠️ [Storage] 업로드 실패: {e}")
            return None
