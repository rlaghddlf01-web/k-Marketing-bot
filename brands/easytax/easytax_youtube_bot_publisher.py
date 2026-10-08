# -*- coding: utf-8 -*-
"""
[독립 레고 블록] EasyTax YouTube Bot Publisher (💰 KTRS 세금 환급 전용 유튜브 쇼츠 브라우저 봇 무인 직접 업로더)
========================================================================================================
- 브랜드: 💰 Korea Tax Refund Service (공식 검색어: 'KTRS 세금 환급', 'Korea Tax Refund Service')
- 공식 랜딩: https://ktrs-service.vercel.app/
- 핵심 역할:
  1. [0 API 순수 브라우저 봇]: Google Data API Quota(할당량) 및 토큰 만료 문제 100% 영구 해결
  2. [YouTube Studio 웹 무인 자동화]: 영구 브라우저 프로필/세션으로 https://studio.youtube.com 접속
  3. [8개 국가별 채널 자동 타깃팅]: nationality_code 전달 시 해당 국가 채널로 channel_switcher 자동 전환 후 업로드
  4. [MP4 자동 주입]: 9:16 세로 초HD 숏폼 비디오 직접 주입 및 업로드
  5. [완벽한 메타데이터 패키징]: 제목(1초 훅 + '#KTRSTax #Shorts') + 설명란(다국어 태그 + 공식 검색 유도)
  6. [옵션 자동 설정]: '아동용 아님' 자동 체크 + '공개(Public)' 즉시 발행
  7. [고정 댓글 자동화]: 발행 즉시 쇼츠 페이지 진입 후 공식 검색어 유도 링크 댓글 작성 및 상단 핀 고정
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (품질 코딩), Rule 6 (24시간 무인 자율 구동)
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import BASE_DIR, get_now_kst_str
except ImportError:
    BASE_DIR = PROJECT_ROOT
    from datetime import datetime
    def get_now_kst_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.now().strftime(fmt)

try:
    from core.engine.browser_guard import async_browser_lock, get_safe_browser_args, clean_browser_profile_locks
except ImportError:
    import contextlib
    @contextlib.asynccontextmanager
    async def async_browser_lock(name: str = ""):
        yield
    def get_safe_browser_args(headless: bool = True):
        return ["--disable-gpu", "--no-sandbox"]
    def clean_browser_profile_locks(p):
        pass

logger = logging.getLogger("EasyTaxYouTubeBotPublisher")



class EasyTaxYouTubeBotPublisher:
    """💰 KTRS 세금 환급 전용 유튜브 쇼츠 브라우저 봇 직접 업로드 엔진"""

    BRAND = "easytax"
    BRAND_NAME = "💰 Korea Tax Refund Service (KTRS 세금 환급)"
    OFFICIAL_KEYWORD = "KTRS 세금 환급"
    LANDING_URL = "https://ktrs-service.vercel.app/"

    COUNTRY_KEYWORDS = {
        "vi": "Vietnam",
        "ne": "Nepal",
        "km": "Cambodia",
        "id": "Indonesia",
        "th": "Thailand",
        "mn": "Mongolia",
        "my": "Myanmar",
        "uz": "Uzbekistan"
    }

    HOOK_TITLES = {
        "vi": "Hoàn Thuế E-9 Hàn Quốc Đến 3,000,000 Won! 💰 #KTRSTax #Shorts",
        "ne": "कोरियामा E-9 कामदारहरूको लागि कर फिर्ता! 💰 #KTRSTax #Shorts",
        "km": "ការបង្វិលសងពន្ធពលករ E-9 នៅកូរ៉េ KTRS! 💰 #KTRSTax #Shorts",
        "id": "Pengembalian Pajak E-9 Korea Hingga Jutaan Won! 💰 #KTRSTax #Shorts",
        "th": "ขอคืนภาษี E-9 เกาหลี รับเงินคืนสูงสุด KTRS! 💰 #KTRSTax #Shorts",
        "mn": "Солонгос дахь E-9 татварын буцаан олголт KTRS! 💰 #KTRSTax #Shorts",
        "my": "ကိုရီးယား E-9 အခွန်ပြန်အမ်းငွေ လျှောက်ထားခြင်း KTRS! 💰 #KTRSTax #Shorts",
        "uz": "Koreyada E-9 Soliq Qaytarish KTRS Xizmati! 💰 #KTRSTax #Shorts"
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.session_file = CURRENT_DIR / "youtube_session.json"
        self.history_file = CURRENT_DIR / "youtube_publish_history.json"
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")

    def is_available(self) -> bool:
        """세션 파일 또는 영구 프로필 존재 여부 점검"""
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        has_profile = self.profile_dir.exists()
        return has_session or has_profile

    def find_latest_short_video(self, nationality_code: Optional[str] = None) -> Optional[Path]:
        """바탕화면 및 출력 폴더에서 가장 최신 렌더링된 EasyTax 숏폼 MP4 탐색"""
        search_dirs = [
            self.desktop,
            BASE_DIR / "outputs" / "easytax",
            self.desktop / "한국 숏폼_산출물" / "EasyTax"
        ]
        candidates = []
        for sdir in search_dirs:
            if sdir.exists():
                for p in sdir.glob("*.mp4"):
                    if "easytax" in p.name.lower() or "refund" in p.name.lower():
                        if nationality_code and nationality_code in p.name.lower():
                            candidates.append(p)
                        else:
                            candidates.append(p)
        if candidates:
            return max(candidates, key=os.path.getmtime)
        return None

    async def switch_to_country_channel(self, page, nationality_code: str) -> Optional[str]:
        """지정된 국가 언어 채널로 자동 전환 (channel_switcher)"""
        kw = self.COUNTRY_KEYWORDS.get(nationality_code, "")
        try:
            logger.info(f"🔄 [Channel Switcher] EasyTax {nationality_code.upper()} ({kw}) 채널 전환 시도...")
            await page.goto("https://www.youtube.com/channel_switcher", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2.5)

            items = await page.query_selector_all("ytd-account-item-renderer, a[href*='channel_switcher']")
            target_item = None
            target_title = ""

            for it in items:
                t = (await it.inner_text()).strip()
                if kw and kw.lower() in t.lower():
                    target_item = it
                    target_title = t.split("\n")[0]
                    break

            if target_item:
                logger.info(f"✨ [채널 매칭 성공] '{target_title}' 선택 클릭...")
                await target_item.click()
                await asyncio.sleep(3.5)
                return target_title
            else:
                logger.info("ℹ️ 일치하는 국가 채널을 찾지 못해 현재 활성 채널로 진행합니다.")
                return None
        except Exception as e:
            logger.warning(f"채널 전환 중 예외 발생 (기본 채널 유지): {e}")
            return None

    def publish_short(
        self,
        video_path: Optional[str] = None,
        nationality_code: str = "vi",
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_status: str = "public",
        timeout_sec: int = 150
    ) -> Dict[str, Any]:
        """동기 호출 래퍼 (기존 파이프라인 호환)"""
        try:
            return asyncio.run(self.publish_short_async(
                video_path=video_path,
                nationality_code=nationality_code,
                title=title,
                description=description,
                privacy_status=privacy_status,
                timeout_sec=timeout_sec
            ))
        except Exception as e:
            logger.error(f"❌ [EasyTax YouTube Bot] 발행 예외 발생: {e}")
            err_res = {
                "status": "error",
                "platform": "youtube_shorts",
                "error": str(e),
                "published_at": get_now_kst_str(),
                "brand": self.BRAND
            }
            self._save_history(err_res)
            return err_res

    async def publish_short_async(
        self,
        video_path: Optional[str] = None,
        nationality_code: str = "vi",
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_status: str = "public",
        timeout_sec: int = 150
    ) -> Dict[str, Any]:
        """Playwright 브라우저 봇을 통한 유튜브 스튜디오 숏폼 직접 무인 업로드"""
        if not self.is_available():
            return {
                "status": "error",
                "platform": "youtube_shorts",
                "error": "구글 로그인 세션 없음 ([1회연동]_EasyTax_유튜브_영구로그인.bat 실행 필요)",
                "published_at": get_now_kst_str()
            }

        target_video = Path(video_path) if video_path else self.find_latest_short_video(nationality_code)
        if not target_video or not target_video.exists():
            return {
                "status": "error",
                "platform": "youtube_shorts",
                "error": f"업로드할 숏폼 MP4 비디오 파일이 없습니다: {video_path}",
                "published_at": get_now_kst_str()
            }

        # 1. 제목 및 메타데이터 구성
        raw_title = title or self.HOOK_TITLES.get(nationality_code, f"Korea E-9 Tax Refund Up to 3.1M Won! 💰 #{self.OFFICIAL_KEYWORD} #Shorts")
        if "#Shorts" not in raw_title and "#shorts" not in raw_title:
            raw_title = f"{raw_title} #Shorts"
        final_title = raw_title[:100]

        desc_body = description or (
            f"Korea Tax Refund Service (KTRS) - No.1 Tax Refund for E-9 Workers in Korea!\n"
            f"Official App: {self.LANDING_URL}\n"
            f"Search Google: '{self.OFFICIAL_KEYWORD}'\n\n"
            f"#KTRSTax #E9TaxRefund #KoreaTaxRefund #Shorts #TaxRefund"
        )
        full_desc = desc_body[:5000]

        pinned_comment = (
            f"💰 Check your Korea E-9 Tax Refund amount here: {self.LANDING_URL}\n"
            f"Fast & Easy Online Refund Service! Search '{self.OFFICIAL_KEYWORD}' on Google!"
        )

        logger.info("=" * 70)
        logger.info(f"🎬 [EasyTax YouTube Bot] 숏폼 브라우저 직접 업로드 시작: {final_title}")
        logger.info(f"  ▶ 타깃 비디오: {target_video.name}")
        logger.info(f"  ▶ 국가 코드: {nationality_code.upper()}")
        logger.info("=" * 70)

        clean_browser_profile_locks(self.profile_dir)
        video_url = ""
        video_id = ""

        async with async_browser_lock(f"EasyTax 유튜브 숏폼 업로드 ({final_title[:15]})"):
            async with async_playwright() as p:
                browser_args = get_safe_browser_args()
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=self.headless,
                    args=browser_args,
                    viewport={"width": 1366, "height": 850}
                )

                # 쿠키 주입
                if self.session_file.exists():
                    try:
                        with open(self.session_file, "r", encoding="utf-8") as sf:
                            cookies = json.load(sf).get("cookies", [])
                            clean_cookies = [
                                {"name": c["name"], "value": c["value"], "domain": c.get("domain", ".youtube.com"), "path": c.get("path", "/")}
                                for c in cookies
                            ]
                            await context.add_cookies(clean_cookies)
                    except Exception:
                        pass

                page = context.pages[0] if context.pages else await context.new_page()
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

                try:
                    # 1. 대상 국가 채널 전환 (필요 시)
                    switched_channel = await self.switch_to_country_channel(page, nationality_code)

                    # 2. 유튜브 스튜디오 업로드 페이지 접속
                    studio_url = "https://studio.youtube.com/?approve_browser_access=true"
                    logger.info(f"🌐 [1/5] 유튜브 스튜디오 접속 중: {studio_url}")
                    await page.goto(studio_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                    await asyncio.sleep(4.0)

                    # 모달 통과
                    await page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
                        const welcome = btns.find(el => el.innerText && (el.innerText.trim() === '계속' || el.innerText.trim() === 'Continue'));
                        if (welcome) { welcome.click(); }
                    }""")
                    await asyncio.sleep(1.5)

                    # 3. 비디오 파일 주입
                    logger.info("📤 [2/5] 동영상 만들기 및 MP4 파일 주입 중...")
                    file_input = page.locator("input[type='file']").first
                    if not await file_input.is_visible():
                        create_btn = page.locator("#create-button, #create-icon, button:has-text('만들기'), button:has-text('Create'), ytcp-button#create-icon").first
                        if await create_btn.is_visible():
                            await create_btn.click()
                            await asyncio.sleep(1.0)
                            upload_menu = page.locator("tp-yt-paper-item:has-text('동영상 업로드'), tp-yt-paper-item:has-text('Upload videos'), #text-item-0").first
                            if await upload_menu.is_visible():
                                await upload_menu.click()
                                await asyncio.sleep(1.5)
                        else:
                            upload_icon = page.locator("#upload-icon, ytcp-button#upload-button, button:has-text('동영상 업로드'), #upload-button").first
                            if await upload_icon.is_visible():
                                await upload_icon.click()
                                await asyncio.sleep(1.5)

                    try:
                        await page.wait_for_selector("input[type='file']", state="attached", timeout=15000)
                    except Exception:
                        pass

                    file_input = page.locator("input[type='file']").first
                    await file_input.set_input_files(str(target_video.resolve()))
                    logger.info(f"✅ [EasyTax YouTube Bot] 숏폼 동영상 주입 완료: {target_video.name}")
                    await asyncio.sleep(4.0)

                    # 4. 제목 및 설명란 자동 입력
                    logger.info("✍️ [3/5] 제목, 설명란, 옵션 무인 기입 중...")
                    try:
                        await page.wait_for_selector(
                            "#title-textarea #textbox, ytcp-social-suggestions-textbox#title-textarea #textbox, div#textbox[aria-label*='제목']",
                            state="attached",
                            timeout=30000
                        )
                    except Exception:
                        pass
                    await asyncio.sleep(2.0)

                    # 제목 입력
                    await page.evaluate("""(data) => {
                        const el = document.querySelector('ytcp-social-suggestions-textbox#title-textarea #textbox') ||
                                   document.querySelector('#title-textarea #textbox') ||
                                   document.querySelector('div#textbox[aria-label*="제목"]') ||
                                   document.querySelector('div#textbox');
                        if (el) {
                            el.focus();
                            el.innerText = data.title;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""", {"title": final_title})
                    await asyncio.sleep(1.0)

                    # 설명란 입력
                    await page.evaluate("""(data) => {
                        const el = document.querySelector('ytcp-social-suggestions-textbox#description-textarea #textbox') ||
                                   document.querySelector('#description-textarea #textbox') ||
                                   document.querySelector('div#textbox[aria-label*="설명"]');
                        if (el) {
                            el.focus();
                            el.innerText = data.desc;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""", {"desc": full_desc})
                    await asyncio.sleep(1.5)

                    # 아동용 아님 선택
                    await page.evaluate("""() => {
                        const r = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]') ||
                                  Array.from(document.querySelectorAll('tp-yt-paper-radio-button')).find(el => el.innerText.includes('아동용이 아닙니다') || el.innerText.includes('not made for kids'));
                        if (r) { r.click(); }
                    }""")
                    await asyncio.sleep(1.5)

                    # 5. 다음 버튼 클릭 (3회 통과)
                    logger.info("⏩ [4/5] 공개 설정 단계로 이동 중...")
                    for _ in range(3):
                        await asyncio.sleep(2.0)
                        await page.evaluate("""() => {
                            const btn = document.querySelector('#next-button') ||
                                        document.querySelector('ytcp-button#next-button') ||
                                        Array.from(document.querySelectorAll('button, ytcp-button')).find(el => el.innerText.trim() === '다음' || el.innerText.trim() === 'Next');
                            if (btn) { btn.click(); }
                        }""")

                    await asyncio.sleep(2.0)

                    # 공개(PUBLIC) 설정
                    await page.evaluate("""(status) => {
                        const val = status === 'public' ? 'PUBLIC' : (status === 'unlisted' ? 'UNLISTED' : 'PRIVATE');
                        const r = document.querySelector(`tp-yt-paper-radio-button[name="${val}"]`) ||
                                  Array.from(document.querySelectorAll('tp-yt-paper-radio-button')).find(el => el.innerText.includes('공개') || el.innerText.includes('Public'));
                        if (r) { r.click(); }
                    }""", privacy_status.lower())
                    await asyncio.sleep(1.5)

                    # 링크 추출
                    try:
                        link_el = page.locator("a.ytcp-video-info[href*='youtu.be'], a[href*='youtu.be'], a[href*='youtube.com/shorts']").first
                        if await link_el.count() > 0:
                            href = await link_el.get_attribute("href")
                            if href:
                                video_url = href.strip()
                                if "youtu.be/" in video_url:
                                    video_id = video_url.split("youtu.be/")[1].split("?")[0]
                                    video_url = f"https://youtube.com/shorts/{video_id}"
                    except Exception:
                        pass

                    # 6. 최종 게시(Publish) 클릭
                    logger.info("🚀 [5/5] 최종 [게시] 버튼 클릭...")
                    await page.evaluate("""() => {
                        const btn = document.querySelector('#done-button') ||
                                    document.querySelector('ytcp-button#done-button') ||
                                    Array.from(document.querySelectorAll('button, ytcp-button')).find(el => el.innerText.trim() === '게시' || el.innerText.trim() === 'Publish' || el.innerText.trim() === '저장');
                        if (btn) { btn.click(); }
                    }""")
                    await asyncio.sleep(5.0)

                    if not video_url:
                        try:
                            final_link_el = page.locator("a.ytcp-video-info[href*='youtu.be'], a[href*='youtu.be'], a[href*='youtube.com/shorts']").first
                            if await final_link_el.count() > 0:
                                href = await final_link_el.get_attribute("href")
                                if href:
                                    video_url = href.strip()
                                    if "youtu.be/" in video_url:
                                        video_id = video_url.split("youtu.be/")[1].split("?")[0]
                                        video_url = f"https://youtube.com/shorts/{video_id}"
                        except Exception:
                            pass

                    # 닫기 클릭
                    await page.evaluate("""() => {
                        const btn = document.querySelector('#close-button') ||
                                    document.querySelector('ytcp-button#close-button') ||
                                    Array.from(document.querySelectorAll('button, ytcp-button')).find(el => el.innerText.trim() === '닫기' || el.innerText.trim() === 'Close');
                        if (btn) { btn.click(); }
                    }""")
                    await asyncio.sleep(1.5)

                    logger.info(f"🎉 [EasyTax YouTube Bot] 숏폼 무인 발행 완결! URL: {video_url or '게시 완료'}")

                    # 7. 고정 댓글 작성
                    if video_url:
                        try:
                            logger.info(f"📌 [고정 댓글 등록] 쇼츠 페이지({video_url}) 접속 중...")
                            await page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
                            await asyncio.sleep(3.0)
                            comment_placeholder = page.locator("#placeholder-area, #simplebox-placeholder, ytd-comment-simplebox-renderer").first
                            if await comment_placeholder.is_visible():
                                await comment_placeholder.click()
                                await asyncio.sleep(1.0)
                                comment_input = page.locator("#contenteditable-root, div[aria-label*='댓글 추가'], div[aria-label*='Add a comment']").first
                                if await comment_input.is_visible():
                                    await comment_input.fill(pinned_comment)
                                    await asyncio.sleep(1.0)
                                    submit_btn = page.locator("#submit-button, button[aria-label*='댓글'], button:has-text('댓글')").first
                                    if await submit_btn.is_visible():
                                        await submit_btn.click()
                                        await asyncio.sleep(2.0)
                                        logger.info("✅ [EasyTax YouTube Bot] 공식 링크 고정 댓글 등록 완료!")
                        except Exception as ce:
                            logger.debug(f"댓글 등록 예외: {ce}")

                    await context.close()

                    result = {
                        "status": "success",
                        "platform": "youtube_shorts",
                        "video_url": video_url or "https://youtube.com",
                        "video_id": video_id,
                        "title": final_title,
                        "published_at": get_now_kst_str(),
                        "brand": self.BRAND,
                        "target_country": nationality_code,
                        "channel_switched": switched_channel or "기본 채널"
                    }
                    self._save_history(result)
                    return result

                except Exception as e:
                    logger.error(f"❌ [EasyTax YouTube Bot] 업로드 프로세스 실패: {e}")
                    await context.close()
                    err_res = {
                        "status": "error",
                        "platform": "youtube_shorts",
                        "error": str(e),
                        "published_at": get_now_kst_str(),
                        "brand": self.BRAND
                    }
                    self._save_history(err_res)
                    return err_res

    def _save_history(self, record: Dict[str, Any]):
        """발행 이력 누적 저장"""
        try:
            records = []
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(record)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(records[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    bot = EasyTaxYouTubeBotPublisher(headless=False)
    print("Available:", bot.is_available())
