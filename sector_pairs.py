# US-KR 섹터 페어 매핑
# apply_market_cap=False → 시총 무관하게 글로벌 동조 로직 적용
SECTOR_PAIRS = [
    {
        "sector": "광통신",
        "us": [
            {"ticker": "LITE",  "name": "Lumentum"},
            {"ticker": "COHR",  "name": "Coherent (II-VI)"},
        ],
        "kr": [
            {"ticker": "001440", "name": "대한광통신"},
            {"ticker": "073490", "name": "이노와이어리스"},
            {"ticker": "036810", "name": "에프에스티"},
        ],
        "apply_market_cap": False,
    },
    {
        "sector": "반도체",
        "us": [
            {"ticker": "MU",    "name": "Micron"},
            {"ticker": "AMAT",  "name": "Applied Materials"},
            {"ticker": "LRCX",  "name": "Lam Research"},
        ],
        "kr": [
            {"ticker": "000660", "name": "SK하이닉스"},
            {"ticker": "005930", "name": "삼성전자"},
            {"ticker": "042700", "name": "한미반도체"},
            {"ticker": "058470", "name": "리노공업"},
            {"ticker": "240810", "name": "원익IPS"},
        ],
        "apply_market_cap": True,
    },
    {
        "sector": "AI/GPU",
        "us": [
            {"ticker": "NVDA",  "name": "NVIDIA"},
            {"ticker": "AMD",   "name": "AMD"},
        ],
        "kr": [
            {"ticker": "042700", "name": "한미반도체"},
            {"ticker": "000660", "name": "SK하이닉스"},
            {"ticker": "196170", "name": "알테오젠"},
        ],
        "apply_market_cap": True,
    },
    {
        "sector": "전력설비",
        "us": [
            {"ticker": "ETN",   "name": "Eaton"},
            {"ticker": "GE",    "name": "GE Vernova"},
            {"ticker": "VRT",   "name": "Vertiv"},
        ],
        "kr": [
            {"ticker": "011690", "name": "LS ELECTRIC"},
            {"ticker": "001680", "name": "대상"},
            {"ticker": "267260", "name": "HD현대일렉트릭"},
            {"ticker": "010120", "name": "LS"},
        ],
        "apply_market_cap": True,
    },
    {
        "sector": "2차전지",
        "us": [
            {"ticker": "TSLA",  "name": "Tesla"},
            {"ticker": "ALB",   "name": "Albemarle"},
        ],
        "kr": [
            {"ticker": "006400", "name": "삼성SDI"},
            {"ticker": "051910", "name": "LG화학"},
            {"ticker": "247540", "name": "에코프로비엠"},
            {"ticker": "086520", "name": "에코프로"},
        ],
        "apply_market_cap": True,
    },
    {
        "sector": "조선",
        "us": [
            {"ticker": "HII",   "name": "Huntington Ingalls"},
        ],
        "kr": [
            {"ticker": "009540", "name": "HD한국조선해양"},
            {"ticker": "010140", "name": "삼성중공업"},
            {"ticker": "042660", "name": "한화오션"},
        ],
        "apply_market_cap": True,
    },
    {
        "sector": "바이오/헬스케어",
        "us": [
            {"ticker": "LLY",   "name": "Eli Lilly"},
            {"ticker": "NVO",   "name": "Novo Nordisk"},
        ],
        "kr": [
            {"ticker": "068270", "name": "셀트리온"},
            {"ticker": "207940", "name": "삼성바이오로직스"},
            {"ticker": "196170", "name": "알테오젠"},
        ],
        "apply_market_cap": True,
    },
]

# 모든 KR 티커 목록 (중복 제거)
def get_all_kr_tickers():
    seen = set()
    result = []
    for pair in SECTOR_PAIRS:
        for item in pair["kr"]:
            if item["ticker"] not in seen:
                seen.add(item["ticker"])
                result.append(item)
    return result

# 모든 US 티커 목록 (중복 제거)
def get_all_us_tickers():
    seen = set()
    result = []
    for pair in SECTOR_PAIRS:
        for item in pair["us"]:
            if item["ticker"] not in seen:
                seen.add(item["ticker"])
                result.append(item)
    return result
