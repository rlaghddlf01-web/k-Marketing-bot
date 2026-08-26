import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, BASE_URLS
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker

logger = logging.getLogger("ProgrammaticSEO")

class ProgrammaticSEO:
    """
    [무인 자동화 3] 전국 모든 대학(30개) + 전국 모든 공단(15개) + 전국 외국인 밀집 동네(20개)
    × 17개국어 × 6대 서비스 대규모 Programmatic SEO & 구글 검색 독점 색인기
    """
    def __init__(self, db_mgr: DBManager):
        self.db_mgr = db_mgr
        self.output_dir = OUTPUTS_DIR / "seo_pages"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.universities = self._load_json(DATA_DIR / "universities.json")
        self.industrials = self._load_json(DATA_DIR / "industrial_complexes.json")
        self.expat_towns = self._load_json(DATA_DIR / "expat_towns.json")
        self.services = self._load_json(DATA_DIR / "services.json")

    def _load_json(self, path: Path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def generate_all_seo_matrix(self) -> int:
        """전국 대학 + 전국 공단 + 전국 외국인 밀집 동네 대규모 SEO 매트릭스 및 sitemap.xml 빌드"""
        generated_count = 0
        sitemap_urls = []

        # 1. 전국 대학 (유학생 타깃) 매트릭스 생성 (30곳)
        for univ in self.universities:
            univ_name_en = univ["name_en"]
            region = univ["region"]

            for service_id, service_info in self.services.items():
                for lang_code, lang_info in LANGUAGES.items():
                    slug = f"univ-{service_id}-{univ_name_en.lower().replace(' ', '-')}-{lang_code}"
                    
                    campaign = UTMTracker.generate_campaign_tag(service_id, "univ_seo", lang_code)
                    target_url = UTMTracker.build_url(
                        base_url=f"{BASE_URLS.get(service_id, 'https://k-market.app')}/campus/{slug}",
                        source="google_seo",
                        medium="campus_landing",
                        campaign=campaign,
                        lang=lang_code
                    )

                    title = f"[{univ_name_en}] {service_info['name']} - Expat Student Guide in {region}"
                    meta_desc = f"Verified expat student guide for {univ_name_en} ({region}). {service_info['description']} in {lang_info['name']}."

                    html_content = self._render_univ_seo_html(title, meta_desc, univ, service_info, lang_info, target_url)
                    
                    page_path = self.output_dir / f"{slug}.html"
                    with open(page_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                    sitemap_urls.append(target_url)
                    generated_count += 1

        # 2. 전국 산업단지 / 공단 (근로자 타깃) 매트릭스 생성 (15곳)
        for ind in self.industrials:
            ind_name_en = ind["name_en"]
            region = ind["region"]
            visas = ", ".join(ind.get("main_visas", ["E-9", "E-7", "F-4"]))

            for service_id, service_info in self.services.items():
                for lang_code, lang_info in LANGUAGES.items():
                    slug = f"industrial-{service_id}-{ind_name_en.lower().replace(' ', '-')}-{lang_code}"
                    
                    campaign = UTMTracker.generate_campaign_tag(service_id, "industrial_seo", lang_code)
                    target_url = UTMTracker.build_url(
                        base_url=f"{BASE_URLS.get(service_id, 'https://k-market.app')}/industrial/{slug}",
                        source="google_seo",
                        medium="industrial_landing",
                        campaign=campaign,
                        lang=lang_code
                    )

                    title = f"[{ind_name_en}] {service_info['name']} - Worker Solution ({visas}) in {region}"
                    meta_desc = f"Essential worker solution for {visas} visa holders at {ind_name_en} ({region}). {service_info['description']} in {lang_info['name']}."

                    html_content = self._render_industrial_seo_html(title, meta_desc, ind, service_info, lang_info, target_url)
                    
                    page_path = self.output_dir / f"{slug}.html"
                    with open(page_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                    sitemap_urls.append(target_url)
                    generated_count += 1

        # 3. 전국 외국인 밀집 거주 동네 / 다문화 특구 (대림동, 가리봉동, 함박마을, 발안 등 20곳)
        for town in self.expat_towns:
            town_name_en = town["name_en"]
            district = town["district"]
            dom_nats = ", ".join(town.get("dominant_nationalities", ["외국인"]))

            for service_id, service_info in self.services.items():
                for lang_code, lang_info in LANGUAGES.items():
                    slug = f"town-{service_id}-{town_name_en.lower().replace(' ', '-').replace('(', '').replace(')', '')}-{lang_code}"
                    
                    campaign = UTMTracker.generate_campaign_tag(service_id, "town_seo", lang_code)
                    target_url = UTMTracker.build_url(
                        base_url=f"{BASE_URLS.get(service_id, 'https://k-market.app')}/town/{slug}",
                        source="google_seo",
                        medium="town_landing",
                        campaign=campaign,
                        lang=lang_code
                    )

                    title = f"[{town_name_en}] {service_info['name']} - Expat Community Hub in {district}"
                    meta_desc = f"Top community solution for {dom_nats} residents at {town['name_ko']} ({district}). {service_info['description']} in {lang_info['name']}."

                    html_content = self._render_town_seo_html(title, meta_desc, town, service_info, lang_info, target_url)
                    
                    page_path = self.output_dir / f"{slug}.html"
                    with open(page_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                    sitemap_urls.append(target_url)
                    generated_count += 1

        # 초거대 Sitemap.xml 생성
        self._generate_sitemap(sitemap_urls)
        logger.info(f"전국 대학(30) + 공단(15) + 외국인 동네(20) 총 {generated_count}개 초거대 SEO 랜딩 빌드 완료")
        return generated_count

    def _render_univ_seo_html(self, title: str, meta_desc: str, univ: Dict[str, Any], 
                              service: Dict[str, Any], lang: Dict[str, Any], target_url: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="{lang.get('name', 'en')}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{target_url}">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8fafc; color: #1e293b; }}
        .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #2563eb; }}
        .badge {{ background: #2563eb; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; display: inline-block; }}
        h1 {{ color: #0f172a; margin-top: 15px; font-size: 24px; }}
        .btn {{ display: inline-block; background: #10b981; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">🎓 University Hub: {univ['name_en']} ({univ['region']})</span>
        <h1>{title}</h1>
        <p>{meta_desc}</p>
        <h3>✨ Student Benefits:</h3>
        <ul>{"".join(f"<li>{usp}</li>" for usp in service.get('usp', []))}</ul>
        <p>Campus hotspots: {', '.join(univ.get('hotspots', []))}</p>
        <a href="{target_url}" class="btn">👉 Access Official Campus Portal</a>
    </div>
</body>
</html>"""

    def _render_industrial_seo_html(self, title: str, meta_desc: str, ind: Dict[str, Any], 
                                    service: Dict[str, Any], lang: Dict[str, Any], target_url: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="{lang.get('name', 'en')}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{target_url}">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8fafc; color: #1e293b; }}
        .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #f59e0b; }}
        .badge {{ background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; display: inline-block; }}
        h1 {{ color: #0f172a; margin-top: 15px; font-size: 24px; }}
        .btn {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">🏭 Industrial Complex: {ind['name_en']} ({ind['region']})</span>
        <h1>{title}</h1>
        <p>{meta_desc}</p>
        <h3>⚙️ Worker Solutions for {', '.join(ind.get('main_visas', []))}:</h3>
        <ul>{"".join(f"<li>{usp}</li>" for usp in service.get('usp', []))}</ul>
        <p>Industrial residential areas: {', '.join(ind.get('hotspots', []))}</p>
        <a href="{target_url}" class="btn">👉 Access Official Industrial Portal</a>
    </div>
</body>
</html>"""

    def _render_town_seo_html(self, title: str, meta_desc: str, town: Dict[str, Any], 
                              service: Dict[str, Any], lang: Dict[str, Any], target_url: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="{lang.get('name', 'en')}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{target_url}">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8fafc; color: #1e293b; }}
        .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #10b981; }}
        .badge {{ background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; display: inline-block; }}
        h1 {{ color: #0f172a; margin-top: 15px; font-size: 24px; }}
        .btn {{ display: inline-block; background: #8b5cf6; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">🏘️ Expat Community Town: {town['name_ko']} ({town['district']})</span>
        <h1>{title}</h1>
        <p>{meta_desc}</p>
        <h3>🌟 Verified Expat Perks for {', '.join(town.get('dominant_nationalities', []))}:</h3>
        <ul>{"".join(f"<li>{usp}</li>" for usp in service.get('usp', []))}</ul>
        <p>Key Neighborhood Areas: {', '.join(town.get('keywords', []))}</p>
        <a href="{target_url}" class="btn">👉 Join {town['name_ko']} Community Hub</a>
    </div>
</body>
</html>"""

    def _generate_sitemap(self, urls: List[str]):
        sitemap_path = self.output_dir / "sitemap.xml"
        items = "".join(f"<url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n" for u in urls[:10000])
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>"""
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
