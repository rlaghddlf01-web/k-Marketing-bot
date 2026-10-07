// ==============================================================================
// [독립 모듈] app_pipelines.js: 대한민국 3대 슈퍼앱 22대 옴니채널 파이프라인 데이터 정의 모듈
// 📈 Stock Master 주식 AI / 💖 Aura AI 데이팅 / 🛡️ InsureBalance 보험비교
// ==============================================================================

const APP_PIPELINES = {
    // --------------------------------------------------------------------------
    // 📈 1. Stock Master 주식 AI 22대 파이프라인
    // --------------------------------------------------------------------------
    stock: {
        brandKey: "stock",
        brandName: "Stock Master (주식 AI)",
        pageTitle: "📈 Stock Master 주식 AI 마케팅 통합 제어 센터",
        pageDesc: "당일 외인/기관 수급 분석, 장전 08:30 시황, 조건검색식, 22개 증시 채널을 24시간 자율 가동합니다.",
        seasonBadge: "STOCK MASTER AI",
        badgeColor: "#FACC15",
        accentColor: "#F59E0B",
        accentBorder: "rgba(245, 158, 11, 0.35)",
        btnGradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
        activeTabBg: "linear-gradient(135deg, #F59E0B, #D97706)",
        
        telegram: {
            title: "📈 Stock Master 텔레그램 24시간 자율 성장 통합 사령부",
            groupName: "Stock Master VIP 시황 (t.me/stockmaster_vip)",
            desc: "외인/기관 실시간 수급 분석 · 08:30 장전 브리핑 · 조건검색식 · 하루 2회(08:40/15:30) 정기 증시 브리핑",
            officialColor: "#F59E0B",
            morningBriefingTitle: "⚡ 장전 VIP 시황 브리핑",
            pollTitle: "📊 종목 토론 투표 1회 생성"
        },

        hubs: [
            // #1 5대 옴니 숏폼 통합 팩토리
            {
                id: "shorts",
                key: "shorts",
                hubNumber: 1,
                name: "🎬 5대 옴니 숏폼 통합 팩토리",
                icon: "🎬",
                desc: "<b>🎬 [영상 AI 1회 렌더링]</b> (9:16 세로 영상 + 감성 배경음악 + AI 음성 TTS + 자막)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 유튜브 쇼츠 (YouTube Shorts)<br>➔ ② 틱톡 (TikTok)<br>➔ ③ 인스타그램 릴스 (Instagram Reels)<br>➔ ④ 페이스북 릴스 (Facebook Reels)<br>➔ ⑤ 네이버 클립 (Naver Clip)</div>"
            },
            // #2 [통합] 4대 옴니 카드뉴스 매거진
            {
                id: "cardnews",
                key: "cardnews",
                hubNumber: 2,
                name: "📸 4대 옴니 카드뉴스 매거진",
                icon: "📸",
                desc: "<b>📸 [카드뉴스 AI 1회 생성]</b> (1080x1350 카드뉴스 세트 + 플랫폼별 최적화 카피)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 인스타그램 피드 (Instagram Feed 캐러셀)<br>➔ ② 페이스북 (Facebook Groups & Feed)<br>➔ ③ 네이버 포스트 (Naver Post 매거진)<br>➔ ④ 스레드 카드뉴스형 (Threads Carousel)</div>"
            },
            // #3 Reddit
            {
                id: "reddit",
                key: "reddit",
                hubNumber: 3,
                name: "🤖 Reddit 글로벌 투자자 2단계 족집게 스텔스 헌터",
                icon: "🤖",
                desc: "<b>🤖 [2단계 족집게 스텔스 헌터]</b> (10대 서브레딧 실시간 스캔 + 1단계 파이썬 100% 심사 + 2단계 제미나이 1회 검증 + 80:20 스텔스 답변)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 타겟 채널: r/stocks, r/investing, r/wallstreetbets, r/algotrading, r/koreanstocks 등 10개<br>➔ ② 안전 쿼터: 홍보 4회 + 비홍보 4회 (하루 5개 분산 세션)<br>➔ ③ 핵심 소구: 외인·기관 쌍끌이 실시간 수급 + AI 퀀트 4대 모달 + Anti-FOMO 리스크 가드<br>➔ ④ 스텔스 원칙: Zero URL + 구글 'StockMaster AI' (또는 '스톡마스터 AI') 검색 유도</div>",
                redditUrl: "https://www.reddit.com/r/stocks/"
            },
            // #5 [통합] 4대 채널 옴니 블로그 통합 허브
            {
                id: "omni_blog",
                key: "omni_blog",
                hubNumber: 5,
                name: "🌐 4대 채널 옴니 블로그 통합 허브",
                icon: "🌐",
                desc: "<b>🌐 [옴니블로그 AI 1회 작성]</b> (제미나이 2,000자 칼럼 + 16:9 이미지 1장 생성)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① Stock Master 본진 피드 (수급/시황 DB)<br>➔ ② 네이버 블로그 (스마트블록 + 16:9 이미지 최우선)<br>➔ ③ 티스토리 (Google SEO 최적화 HTML)<br>➔ ④ 카카오 브런치 (증시 리포트 에세이)</div>"
            },
            // #6 [통합] 2대 포털 검색엔진 동시 색인 핑 (구글 + 네이버)
            {
                id: "seo",
                key: "seo",
                hubNumber: 6,
                name: "🌐 2대 검색엔진 동시 색인 핑 허브",
                icon: "🌐",
                desc: "<b>🌐 [검색엔진 동시 색인 핑]</b> (신규 콘텐츠 즉시 수집 요청 & 색인 가속)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 구글 서치콘솔 (Google Search Console & Googlebot 실시간 색인 핑)<br>➔ ② 네이버 서치어드바이저 (Naver Search Advisor & Yeti 봇 즉시 수집 요청)</div>",
                isSeo: true,
                googleConsoleUrl: "https://search.google.com/search-console",
                naverAdvisorUrl: "https://searchadvisor.naver.com/console/board",
                sitemapUrl: "https://stockmaster-ai.vercel.app/sitemap.xml",
                domainUrl: "https://stockmaster-ai.vercel.app/"
            },
            // #7 [통합] 2대 텍스트 스토리 타래 허브 (Threads + X)
            {
                id: "threads",
                key: "threads",
                hubNumber: 7,
                name: "📜 2대 텍스트 스토리 타래 허브",
                icon: "📜",
                desc: "<b>📜 [텍스트 스토리 AI 1회 생성]</b> (광고 티 0% 증시 실전 수급 인사이트 타래)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① Meta 스레드 (Threads 1/n 줄줄이 타래 썰 + 첫댓글 링크)<br>➔ ② X / 트위터 (Twitter/X API v2 1/n 바이럴 타래 스레드)</div>"
            },
            // #14 네이버 지식iN
            {
                id: "naver_kin",
                key: "naver_kin",
                hubNumber: 14,
                name: "네이버 지식iN 실시간 낚아채기",
                icon: "💡",
                desc: "\"00전자 목표가\", \"00주식 전망\" 실시간 질문 감지 및 답변"
            },
            // #15 네이버 카페
            {
                id: "naver_cafe",
                key: "naver_cafe",
                hubNumber: 15,
                name: "네이버 카페 (5일 로테이션)",
                icon: "☕",
                desc: "30만 대형 주식 카페 5일 쿨다운 안티밴 준수 자연스러운 바이럴"
            },
            // #16 다음 카페
            {
                id: "daum_cafe",
                key: "daum_cafe",
                hubNumber: 16,
                name: "다음(Daum) 카페 (감성 썰)",
                icon: "🍵",
                desc: "대형 다음 카페 외인/기관 순매수 분석 정보글 투고"
            },
            // #17 뽐뿌 포럼
            {
                id: "ppomppu",
                key: "ppomppu",
                hubNumber: 17,
                name: "뽐뿌 포럼 (커뮤니티 팩트)",
                icon: "🛒",
                desc: "증권포럼 당일 실전 매매일지 및 수급 특징주 정보글"
            },
            // #18 디시인사이드
            {
                id: "dcinside",
                key: "dcinside",
                hubNumber: 18,
                name: "디시인사이드 (OCR 돌파)",
                icon: "갤",
                desc: "주식 갤러리/미주갤 한글 초성 캡차 자동 돌파 정보글 투고"
            },
            // #19 보배드림
            {
                id: "bobaedream",
                key: "bobaedream",
                hubNumber: 19,
                name: "보배드림 (베스트글 공략)",
                icon: "🚗",
                desc: "직장인 개미 매매일지 및 시장 분석 베스트글 공략"
            },
            // #20 네이트판
            {
                id: "nate_pann",
                key: "nate_pann",
                hubNumber: 20,
                name: "네이트판 (톡커들의 선택)",
                icon: "💬",
                desc: "주식 물린 개미 탈출 실전 팁 및 멘탈 관리 썰 투고"
            },
            // #21 에펨코리아
            {
                id: "fmkorea",
                key: "fmkorea",
                hubNumber: 21,
                name: "에펨코리아(펨코)",
                icon: "⚽",
                desc: "펨코 주식 갤러리 맞춤형 장중 시황 요약 및 수급 분석"
            },
            // #22 카카오 알림톡
            {
                id: "kakao_channel",
                key: "kakao_channel",
                hubNumber: 22,
                name: "카카오 알림톡 & 채널",
                icon: "💬",
                desc: "장전 08:30 시황 알림톡 · 당일 주도 테마주 속보 발송"
            }
        ]
    },

    // --------------------------------------------------------------------------
    // 💖 2. Aura (AI 데이팅) 22대 파이프라인
    // --------------------------------------------------------------------------
    aura: {
        brandKey: "aura",
        brandName: "Aura (AI 데이팅)",
        pageTitle: "💖 Aura AI 데이팅 마케팅 통합 제어 센터",
        pageDesc: "2030 소개팅 팁, 연애 심리 칼럼, 릴스/숏폼, 22개 소셜 채널을 24시간 자율 가동합니다.",
        seasonBadge: "AURA DATING",
        badgeColor: "#EC4899",
        accentColor: "#EC4899",
        accentBorder: "rgba(236, 72, 153, 0.35)",
        btnGradient: "linear-gradient(135deg, #EC4899 0%, #BE185D 100%)",
        activeTabBg: "linear-gradient(135deg, #EC4899, #BE185D)",

        telegram: {
            title: "💖 Aura 데이팅 텔레그램 24시간 자율 성장 통합 사령부",
            groupName: "Aura Dating VIP (t.me/aura_dating_official)",
            desc: "2030 솔로 미팅 & 소개팅 코칭 · 실시간 Q&A · 주말 매칭 알림 · 하루 2회(12:00/21:00) 정기 브리핑",
            officialColor: "#EC4899",
            morningBriefingTitle: "⚡ 연애 심리 모닝 브리핑",
            pollTitle: "📊 연애 취향 투표 1회 생성"
        },

        hubs: [
            // #1 5대 옴니 숏폼 통합 팩토리
            {
                id: "shorts",
                key: "shorts",
                hubNumber: 1,
                name: "🎬 5대 옴니 숏폼 통합 팩토리",
                icon: "🎬",
                desc: "<b>🎬 [8대 주제 무인 순차 렌더링]</b> (1번 탈출전화 ~ 8번 안심레이더 8개 숏폼 전편 순차 제작 + 5대 SNS 포스팅 가이드 자동 생성)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 유튜브 쇼츠 (YouTube Shorts)<br>➔ ② 틱톡 (TikTok)<br>➔ ③ 인스타그램 릴스 (Instagram Reels)<br>➔ ④ 페이스북 릴스 (Facebook Reels)<br>➔ ⑤ 네이버 클립 (Naver Clip)</div>"
            },
            // #2 [통합] 4대 옴니 카드뉴스 매거진
            {
                id: "cardnews",
                key: "cardnews",
                hubNumber: 2,
                name: "📸 4대 옴니 카드뉴스 매거진",
                icon: "📸",
                desc: "<b>📸 [카드뉴스 AI 1회 생성]</b> (1080x1350 카드뉴스 세트 + 플랫폼별 최적화 카피)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 인스타그램 피드 (Instagram Feed 캐러셀)<br>➔ ② 페이스북 (Facebook Groups & Feed)<br>➔ ③ 네이버 포스트 (Naver Post 매거진)<br>➔ ④ 스레드 카드뉴스형 (Threads Carousel)</div>"
            },
            // #3 Reddit
            {
                id: "reddit",
                key: "reddit",
                hubNumber: 3,
                name: "🤖 Reddit 글로벌 여성 2단계 족집게 스텔스 헌터",
                icon: "🤖",
                desc: "<b>🤖 [2단계 족집게 스텔스 헌터]</b> (12대 서브레딧 실시간 스캔 + 1단계 파이썬 100% 심사 + 2단계 제미나이 1회 검증 + 80:20 스텔스 답변)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 연동 계정: <strong>u/seoul_chloe_</strong> (영구 세션 유지 🟢)<br>➔ ② 타겟 채널: r/Language_Exchange, r/Korean, r/koreatravel 등 12개<br>➔ ③ 안전 쿼터: 홍보 4회 + 비홍보 4회 (하루 5개 분산 세션)<br>➔ ④ 스텔스 원칙: Zero URL + 구글 'Aura AI Dating' 듀얼 검색 유도</div>",
                redditUrl: "https://www.reddit.com/user/seoul_chloe_/comments/"
            },
            // #5 [통합] 4대 채널 옴니 블로그 통합 허브
            {
                id: "omni_blog",
                key: "omni_blog",
                hubNumber: 5,
                name: "💖 4대 채널 옴니 블로그 통합 허브",
                icon: "💖",
                desc: "<b>💖 [옴니블로그 AI 1회 작성]</b> (제미나이 2,000자 칼럼 + 16:9 감성 사진 1장 생성)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① Aura 앱 라운지 피드 (4개국어 자동 배포)<br>➔ ② 네이버 블로그 (스마트블록 + 16:9 사진 최우선)<br>➔ ③ 티스토리 (Google SEO 최적화 HTML)<br>➔ ④ 카카오 브런치 (감성 에세이 작가 채널)</div>"
            },
            // #6 [통합] 2대 포털 검색엔진 동시 색인 핑 (구글 + 네이버)
            {
                id: "seo",
                key: "seo",
                hubNumber: 6,
                name: "🌐 2대 검색엔진 동시 색인 핑 허브",
                icon: "🌐",
                desc: "<b>🌐 [검색엔진 동시 색인 핑]</b> (7,005개 URL 즉시 수집 요청 & 색인 가속)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 구글 서치콘솔 (7,005개 색인 팡 제출 완료 & Googlebot 실시간 색인 핑)<br>➔ ② 네이버 서치어드바이저 (소유권 인증 완료 & Yeti 봇 즉시 수집 요청)</div>",
                isSeo: true,
                googleConsoleUrl: "https://search.google.com/search-console",
                naverAdvisorUrl: "https://searchadvisor.naver.com/console/board",
                sitemapUrl: "https://aura-ai-dating.vercel.app/sitemap_aura.xml",
                domainUrl: "https://aura-ai-dating.vercel.app/"
            },
            // #7 [통합] 2대 텍스트 스토리 타래 허브 (Threads + X)
            {
                id: "threads",
                key: "threads",
                hubNumber: 7,
                name: "📜 2대 텍스트 스토리 타래 허브",
                icon: "📜",
                desc: "<b>📜 [텍스트 스토리 AI 1회 생성]</b> (광고 티 0% 주식 투자 성공/실패 & 퀀트 매매 실화 썰)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① Meta 스레드 (Threads 1/n 줄줄이 타래 썰 + 첫댓글 링크)<br>➔ ② X / 트위터 (Twitter/X API v2 1/n 바이럴 타래 스레드)</div>"
            },
            // #14 네이버 지식iN
            {
                id: "naver_kin",
                key: "naver_kin",
                hubNumber: 14,
                name: "💡 네이버 지식iN 100대 황금키워드 낚아채기",
                icon: "💡",
                desc: "<b>💡 [100대 황금키워드 실시간 레이더]</b> (국내/미국 주식/ETF/AI 퀀트 100개 키워드 실시간 스캔 + 85점 심사 + 10년 차 수석 애널리스트 3박자 킬러 답변)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 100대 황금 키워드 실시간 질문 낚아채기 (하루 딱 10개 엄선)<br>➔ ② Gemini 2.5 Flash 적합도 85점 이상 선별 (불법 리딩방 100% 차단)<br>➔ ③ 10년 차 애널리스트 3박자 답변 (종목분석 70% + 리딩방피해 15% + StockMaster 15%)</div>",
                isKin: true,
                kinUrl: "https://kin.naver.com"
            },
            // #15 네이버 카페
            {
                id: "naver_cafe",
                key: "naver_cafe",
                hubNumber: 15,
                name: "네이버 카페 (5일 로테이션)",
                icon: "☕",
                desc: "30만 대형 2030 친목/직장인 카페 5일 쿨다운 안티밴 바이럴"
            },
            // #16 다음 카페
            {
                id: "daum_cafe",
                key: "daum_cafe",
                hubNumber: 16,
                name: "다음(Daum) 카페 (감성 썰)",
                icon: "🍵",
                desc: "대형 다음 카페 현실 공감 연애 썰 및 소개팅 팁 투고"
            },
            // #17 뽐뿌 포럼
            {
                id: "ppomppu",
                key: "ppomppu",
                hubNumber: 17,
                name: "뽐뿌 포럼 (커뮤니티 팩트)",
                icon: "🛒",
                desc: "자유게시판 솔로 탈출 공감 썰 · 소개팅 후기 정보글"
            },
            // #18 디시인사이드
            {
                id: "dcinside",
                key: "dcinside",
                hubNumber: 18,
                name: "디시인사이드 (OCR 돌파)",
                icon: "갤",
                desc: "연애 갤러리 한글 초성 캡차 자동 돌파 정보글 투고"
            },
            // #19 보배드림
            {
                id: "bobaedream",
                key: "bobaedream",
                hubNumber: 19,
                name: "보배드림 (베스트글 공략)",
                icon: "🚗",
                desc: "3040 현실 연애 팁 및 데이트 코스 정보글"
            },
            // #20 네이트판
            {
                id: "nate_pann",
                key: "nate_pann",
                hubNumber: 20,
                name: "네이트판 (톡커들의 선택)",
                icon: "💬",
                desc: "102030 공감 폭발 연애 썰 및 썸 탈출 실전 팁"
            },
            // #21 에펨코리아
            {
                id: "fmkorea",
                key: "fmkorea",
                hubNumber: 21,
                name: "에펨코리아(펨코)",
                icon: "⚽",
                desc: "2030 남성 맞춤형 유쾌한 소개팅 팁 및 대화법"
            },
            // #22 카카오 알림톡
            {
                id: "kakao_channel",
                key: "kakao_channel",
                hubNumber: 22,
                name: "카카오 알림톡 & 채널",
                icon: "💬",
                desc: "금요일 저녁 주말 맞춤 매칭 안내 및 코칭 알림톡"
            }
        ]
    },

    // --------------------------------------------------------------------------
    // 🛡️ 3. InsureBalance (보험 비교) 22대 파이프라인
    // --------------------------------------------------------------------------
    insurance: {
        brandKey: "insurance",
        brandName: "InsureBalance (보험비교)",
        pageTitle: "🛡️ InsureBalance 보험비교 마케팅 통합 제어 센터",
        pageDesc: "실손보험 비교, 3대 질병 절약 가이드, 호갱 탈출 팁, 22개 채널을 24시간 자율 가동합니다.",
        seasonBadge: "INSUREBALANCE",
        badgeColor: "#10B981",
        accentColor: "#10B981",
        accentBorder: "rgba(16, 185, 129, 0.35)",
        btnGradient: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
        activeTabBg: "linear-gradient(135deg, #10B981, #059669)",

        telegram: {
            title: "🛡️ InsureBalance 텔레그램 24시간 자율 성장 통합 사령부",
            groupName: "InsureBalance 케어 (t.me/insurebalance_official)",
            desc: "실손보험 비교 & 호갱 탈출 가이드 · 3대 질병 절약 팁 · 실시간 보험 분석 · 하루 2회(09:00/18:00) 정기 브리핑",
            officialColor: "#10B981",
            morningBriefingTitle: "⚡ 보험 절약 모닝 브리핑",
            pollTitle: "📊 보험 만족도 투표 1회 생성"
        },

        hubs: [
            // #1 5대 옴니 숏폼 통합 팩토리
            {
                id: "shorts",
                key: "shorts",
                hubNumber: 1,
                name: "🎬 5대 옴니 숏폼 통합 팩토리",
                icon: "🎬",
                desc: "<b>🎬 [영상 AI 1회 렌더링]</b> (9:16 세로 영상 + 감성 배경음악 + AI 음성 TTS + 자막)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 유튜브 쇼츠 (YouTube Shorts)<br>➔ ② 틱톡 (TikTok)<br>➔ ③ 인스타그램 릴스 (Instagram Reels)<br>➔ ④ 페이스북 릴스 (Facebook Reels)<br>➔ ⑤ 네이버 클립 (Naver Clip)</div>"
            },
            // #2 [통합] 4대 옴니 카드뉴스 매거진
            {
                id: "cardnews",
                key: "cardnews",
                hubNumber: 2,
                name: "📸 4대 옴니 카드뉴스 매거진",
                icon: "📸",
                desc: "<b>📸 [카드뉴스 AI 1회 생성]</b> (1080x1350 카드뉴스 세트 + 플랫폼별 최적화 카피)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 인스타그램 피드 (Instagram Feed 캐러셀)<br>➔ ② 페이스북 (Facebook Groups & Feed)<br>➔ ③ 네이버 포스트 (Naver Post 매거진)<br>➔ ④ 스레드 카드뉴스형 (Threads Carousel)</div>"
            },
            // #3 Reddit
            {
                id: "reddit",
                key: "reddit",
                hubNumber: 3,
                name: "🤖 Reddit 외국인·유학생 2단계 족집게 스텔스 헌터",
                icon: "🤖",
                desc: "<b>🤖 [2단계 족집게 스텔스 헌터]</b> (10대 서브레딧 실시간 스캔 + 1단계 파이썬 100% 심사 + 2단계 제미나이 1회 검증 + 80:20 스텔스 답변)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 타겟 채널: r/Living_in_Korea, r/teachinginkorea, r/korea 등 10개<br>➔ ② 안전 쿼터: 홍보 4회 + 비홍보 4회 (하루 5개 분산 세션)<br>➔ ③ 핵심 소구: NHIS vs 4세대 실손 + 비급여(MRI/도수) 80~90% 환급 + 전화스팸 0%<br>➔ ④ 스텔스 원칙: Zero URL + 구글 '보험 리밸런스' 검색 유도</div>",
                redditUrl: "https://www.reddit.com/r/Living_in_Korea/"
            },
            // #5 [통합] 4대 채널 옴니 블로그 통합 허브
            {
                id: "omni_blog",
                key: "omni_blog",
                hubNumber: 5,
                name: "🛡️ 4대 채널 옴니 블로그 통합 허브",
                icon: "🛡️",
                desc: "<b>🛡️ [옴니블로그 AI 1회 작성]</b> (제미나이 2,000자 칼럼 + 16:9 감성 사진 1장 생성)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① InsureBalance 본진 피드 (보험 비교 DB)<br>➔ ② 네이버 블로그 (스마트블록 + 16:9 사진 최우선)<br>➔ ③ 티스토리 (Google SEO 최적화 HTML)<br>➔ ④ 카카오 브런치 (보험 절약 전문 에세이)</div>"
            },
            // #6 [통합] 2대 포털 검색엔진 동시 색인 핑 (구글 + 네이버)
            {
                id: "seo",
                key: "seo",
                hubNumber: 6,
                name: "🌐 2대 검색엔진 동시 색인 핑 허브",
                icon: "🌐",
                desc: "<b>🌐 [검색엔진 동시 색인 핑]</b> (신규 콘텐츠 즉시 수집 요청 & 색인 가속)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 구글 서치콘솔 (Google Search Console & Googlebot 실시간 색인 핑)<br>➔ ② 네이버 서치어드바이저 (Naver Search Advisor & Yeti 봇 즉시 수집 요청)</div>",
                isSeo: true,
                googleConsoleUrl: "https://search.google.com/search-console",
                naverAdvisorUrl: "https://searchadvisor.naver.com/console/board",
                sitemapUrl: "https://insure-balance.vercel.app/sitemap.xml",
                domainUrl: "https://insure-balance.vercel.app/"
            },
            // #7 [통합] 2대 텍스트 스토리 타래 허브 (Threads + X)
            {
                id: "threads",
                key: "threads",
                hubNumber: 7,
                name: "📜 2대 텍스트 스토리 타래 허브",
                icon: "📜",
                desc: "<b>📜 [텍스트 스토리 AI 1회 생성]</b> (광고 티 0% 보험 호갱 탈출 & 실손 청구 실화 썰)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① Meta 스레드 (Threads 1/n 줄줄이 타래 썰 + 첫댓글 링크)<br>➔ ② X / 트위터 (Twitter/X API v2 1/n 바이럴 타래 스레드)</div>"
            },
            // #14 네이버 지식iN
            {
                id: "naver_kin",
                key: "naver_kin",
                hubNumber: 14,
                name: "💡 네이버 지식iN 100대 황금키워드 낚아채기",
                icon: "💡",
                desc: "<b>💡 [100대 황금키워드 실시간 레이더]</b> (실손/암/뇌심/운전자/리모델링 100개 키워드 실시간 스캔 + 85점 심사 + 12년 차 컨설턴트 3박자 킬러 답변)<br><div style='margin-top:6px; background:#FFFFFF; border:1px solid #E5DDD1; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.55; color:#4A443D;'>➔ ① 100대 황금 키워드 실시간 질문 낚아채기 (하루 딱 10개 엄선)<br>➔ ② Gemini 2.5 Flash 적합도 85점 이상 선별 (보험사기 100% 차단)<br>➔ ③ 12년 차 공인 컨설턴트 3박자 답변 (증권분석 70% + 눈탱이피해 15% + InsureBalance 15%)</div>",
                isKin: true,
                kinUrl: "https://kin.naver.com"
            },
            // #15 네이버 카페
            {
                id: "naver_cafe",
                key: "naver_cafe",
                hubNumber: 15,
                name: "네이버 카페 (5일 로테이션)",
                icon: "☕",
                desc: "30만 대형 재테크/맘카페 5일 쿨다운 안티밴 준수 정보 공유"
            },
            // #16 다음 카페
            {
                id: "daum_cafe",
                key: "daum_cafe",
                hubNumber: 16,
                name: "다음(Daum) 카페 (감성 썰)",
                icon: "🍵",
                desc: "대형 다음 카페 월 15만원 절약한 보험 리모델링 후기"
            },
            // #17 뽐뿌 포럼
            {
                id: "ppomppu",
                key: "ppomppu",
                hubNumber: 17,
                name: "뽐뿌 포럼 (커뮤니티 팩트)",
                icon: "🛒",
                desc: "보험포럼 불필요 특약 분석 및 가성비 플랜 정보글"
            },
            // #18 디시인사이드
            {
                id: "dcinside",
                key: "dcinside",
                hubNumber: 18,
                name: "디시인사이드 (OCR 돌파)",
                icon: "갤",
                desc: "보험 갤러리 한글 초성 캡차 자동 돌파 및 정보글 투고"
            },
            // #19 보배드림
            {
                id: "bobaedream",
                key: "bobaedream",
                hubNumber: 19,
                name: "보배드림 (베스트글 공략)",
                icon: "🚗",
                desc: "교통사고 처리 팁 & 변호사 선임비용 운전자보험 팁"
            },
            // #20 네이트판
            {
                id: "nate_pann",
                key: "nate_pann",
                hubNumber: 20,
                name: "네이트판 (톡커들의 선택)",
                icon: "💬",
                desc: "설계사 지인한테 당한 보험 리모델링 성공 썰 투고"
            },
            // #21 에펨코리아
            {
                id: "fmkorea",
                key: "fmkorea",
                hubNumber: 21,
                name: "에펨코리아(펨코)",
                icon: "⚽",
                desc: "사회초년생 첫 보험 필수 체크리스트 요약 정보글"
            },
            // #22 카카오 알림톡
            {
                id: "kakao_channel",
                key: "kakao_channel",
                hubNumber: 22,
                name: "카카오 알림톡 & 채널",
                icon: "💬",
                desc: "기존 증권 1:1 무료 분석 접수 및 맞춤 절약 플랜"
            }
        ]
    }
};

window.APP_PIPELINES = APP_PIPELINES;
