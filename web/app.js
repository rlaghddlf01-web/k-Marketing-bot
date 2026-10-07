// ==========================================
// [메인 진입점] app.js: 전체 모듈 초기화 및 라이프사이클 관리
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    // 1. 탭 네비게이션 초기화
    if (typeof initTabs === "function") initTabs();

    // 2. 기본 브랜드(💖 Aura AI 데이팅)로 스위처 및 헤더 초기화
    if (typeof switchBrand === "function") switchBrand(currentBrand || "aura");

    // 3. 대시보드 22대 허브 그리드 초기 렌더링
    if (typeof renderHubGrid === "function") renderHubGrid();

    // 4. 실시간 서버 상태 초기 조회
    if (typeof fetchStatus === "function") fetchStatus();

    // 5. 텔레그램 통합 사령부 초기 로드
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();

    // 6. 각 탭별 초기 데이터 로드
    if (typeof loadPlatforms === "function") loadPlatforms();
    if (typeof loadGallery === "function") loadGallery();
    if (typeof loadGoldenCopies === "function") loadGoldenCopies();
    if (typeof loadSettings === "function") loadSettings();

    // 7. 3초 주기 실시간 상태 자동 폴링
    setInterval(() => {
        if (typeof fetchStatus === "function") fetchStatus();
    }, 3000);

    console.log("🚀 3대 슈퍼앱 마케팅 사령부가 성공적으로 초기화되었습니다.");
});
