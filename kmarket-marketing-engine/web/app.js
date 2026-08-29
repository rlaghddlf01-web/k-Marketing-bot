// ==========================================
// [메인 진입점] app.js: 전체 모듈 초기화 및 라이프사이클 관리
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    // 1. 탭 네비게이션 초기화
    if (typeof initTabs === "function") initTabs();

    // 2. 대시보드 8대 허브 그리드 초기 렌더링
    if (typeof renderHubGrid === "function") renderHubGrid();

    // 3. 실시간 서버 상태 초기 조회
    if (typeof fetchStatus === "function") fetchStatus();

    // 4. 각 탭별 초기 데이터 로드
    if (typeof loadPlatforms === "function") loadPlatforms();
    if (typeof loadGallery === "function") loadGallery();
    if (typeof loadGoldenCopies === "function") loadGoldenCopies();
    if (typeof loadSettings === "function") loadSettings();

    // 5. 3초 주기 실시간 상태 자동 폴링
    setInterval(() => {
        if (typeof fetchStatus === "function") fetchStatus();
    }, 3000);

    console.log("🚀 KTRS 마케팅 봇 컨트롤 센터가 모든 모듈과 함께 성공적으로 로드되었습니다.");
});
