import os

# Telegram
BOT_TOKEN = "8524664770:AAE7Mx-BNKVifWhqpq6IveK_pGIqZl4YR04"
CHAT_ID   = "381931611"

# Cloudflare Pages URL (Cloudflare 세팅 후 변경)
DASHBOARD_URL = "https://leading-stock.pages.dev"

# 신호 임계값
VOLUME_RATIO_MIN         = 1.5   # 거래량 / 20일 평균
FOREIGN_PERCENTILE_MIN   = 70    # 최근 60일 중 상위 N% (70 = 상위 30%)
HIGH52W_THRESHOLD        = 0.97  # 52주 고가 대비 현재가 비율

# 시총 기준 (한국 독립 주도주에만 적용)
LARGE_CAP_KRW = 5_000_000_000_000  # 5조

# 시총별 LATE 기준
LATE_LARGE  = {"kr_5d": 15.0, "kr_10d": 25.0}   # 시총 1조+
LATE_SMALL  = {"kr_5d": 20.0, "kr_10d": 40.0}   # 시총 1조 미만

# BUY READY 조건
BUY_READY = {
    "us_5d_min":  7.0,
    "kr_5d_min":  5.0,
    "kr_10d_max": 20.0,
}

# WATCH 조건
WATCH = {
    "us_5d_min":  5.0,
    "kr_5d_min":  3.0,
    "kr_5d_max":  5.0,
}

# 데이터 수집 기간
HISTORY_DAYS = 90   # 52주 고가, 60일 외국인 수급 계산용

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
