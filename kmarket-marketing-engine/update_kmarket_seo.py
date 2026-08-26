from pathlib import Path

layout_path = Path(r"C:\Users\zkfnt\Desktop\k-market\src\app\layout.tsx")
content = layout_path.read_text(encoding="utf-8")

# 1. Title 변경
content = content.replace(
    "title: 'KTRS K-Market (케이마켓) | 외국인 중고거래 & 무빙세일',",
    "title: 'KTRS K-Market (케이마켓) | 외국인 0원 무료 나눔 & 중고거래 무빙세일',",
)

# 2. Description 변경
content = content.replace(
    "대한민국 No.1 외국인 근로자 전용 0원 수수료 중고거래 & 귀국 무빙세일 플랫폼! 17개국어 실시간 자동 번역 채팅, 평택·안산·화성 전국 공단 도보 5분 안심 직거래, 최대 1000만원 세금 환급 원스톱 연계",
    "대한민국 No.1 외국인 0원 무료 나눔 & 중고거래 무빙세일 플랫폼! 17개국어 실시간 자동 번역 채팅, 대학가·공단 도보 5분 안심 직거래, 최대 1000만원 세금 환급 원스톱 연계",
)

# 3. OpenGraph 변경
content = content.replace(
    "title: 'KTRS K-Market (케이마켓) | 외국인 중고거래 & 무빙세일',",
    "title: 'KTRS K-Market (케이마켓) | 외국인 0원 무료 나눔 & 중고거래 무빙세일',",
)
content = content.replace(
    "대한민국 No.1 외국인 근로자 전용 0원 수수료 중고거래 & 귀국 무빙세일 플랫폼! 17개국어 실시간 번역 채팅 및 공단 안심 직거래",
    "대한민국 No.1 외국인 0원 무료 나눔 & 중고거래 무빙세일 플랫폼! 17개국어 실시간 번역 채팅 및 공단·대학가 안심 직거래",
)

# 4. Keywords 변경
content = content.replace(
    "'K-Market,케이마켓,KTRS,외국인 중고거래,무빙세일,Moving Sale,세금환급,17개국어 번역 채팅,평택 포승공단,안산 반월공단'",
    "'K-Market,케이마켓,0원 무료 나눔,무료나눔,외국인 중고거래,무빙세일,Moving Sale,Free Giveaway,세금환급,17개국어 번역 채팅'",
)

layout_path.write_text(content, encoding="utf-8")
print("SUCCESS: 0원 무료 나눔 키워드 추가 완료")
