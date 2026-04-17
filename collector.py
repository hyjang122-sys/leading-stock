"""
데이터 수집: FinanceDataReader(OHLCV+시총) + Naver 스크래핑(외국인수급) + yfinance(US)
"""
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import yfinance as yf
from sector_pairs import get_all_kr_tickers, get_all_us_tickers

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

_listing_cache = {}

def _get_listing():
    if _listing_cache:
        return _listing_cache["df"]
    kospi = fdr.StockListing("KOSPI")
    kosdaq = fdr.StockListing("KOSDAQ")
    df = pd.concat([kospi, kosdaq], ignore_index=True)
    _listing_cache["df"] = df
    return df

def _get_marcap(ticker: str) -> int:
    df = _get_listing()
    row = df[df["Code"] == ticker]
    if row.empty:
        return 0
    return int(row.iloc[0]["Marcap"])

def _fetch_naver_foreign(ticker: str, pages: int = 3) -> pd.DataFrame:
    """
    네이버 금융 외국인/기관 순매매 테이블 파싱
    반환: DataFrame(날짜, 종가, 거래량, 기관, 외국인)
    """
    rows = []
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/item/frgn.naver?code={ticker}&page={page}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            table = None
            for t in soup.find_all("table"):
                if "외국인 기관 순매매 거래량" in t.text:
                    table = t
                    break
            if not table:
                break
            for tr in table.find_all("tr")[2:]:
                tds = tr.find_all("td")
                if len(tds) < 7:
                    continue
                date_txt = tds[0].text.strip()
                if not re.match(r"\d{4}\.\d{2}\.\d{2}", date_txt):
                    continue
                def _n(td):
                    t = td.text.strip().replace(",", "").replace("+", "").replace("%", "")
                    try:
                        return int(t) if t and t != "-" else 0
                    except ValueError:
                        return 0
                rows.append({
                    "date":    date_txt,
                    "close":   _n(tds[1]),
                    "volume":  _n(tds[4]),
                    "inst":    _n(tds[5]),
                    "foreign": _n(tds[6]),
                })
        except Exception as e:
            print(f"  [naver] {ticker} page{page} 오류: {e}")
        time.sleep(0.3)

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y.%m.%d")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def fetch_kr_data() -> dict:
    """
    KR 종목별 신호 계산용 데이터 반환
    """
    kr_tickers = get_all_kr_tickers()
    result = {}

    for item in kr_tickers:
        ticker = item["ticker"]
        name   = item["name"]
        try:
            # OHLCV (FDR)
            ohlcv = fdr.DataReader(ticker, (datetime.today() - timedelta(days=300)).strftime("%Y-%m-%d"))
            if ohlcv.empty or len(ohlcv) < 11:
                continue

            close_now  = float(ohlcv["Close"].iloc[-1])
            close_5d   = float(ohlcv["Close"].iloc[-6])  if len(ohlcv) >= 6  else close_now
            close_10d  = float(ohlcv["Close"].iloc[-11]) if len(ohlcv) >= 11 else close_now
            high52w    = float(ohlcv["High"].max())
            vol_today  = float(ohlcv["Volume"].iloc[-1])
            vol_20d    = float(ohlcv["Volume"].iloc[-21:-1].mean()) if len(ohlcv) >= 21 else vol_today

            price_5d  = (close_now / close_5d  - 1) * 100
            price_10d = (close_now / close_10d - 1) * 100
            vol_ratio = vol_today / vol_20d if vol_20d > 0 else 0

            # 시가총액
            mktcap = _get_marcap(ticker)

            # 외국인 순매수 (Naver)
            fi = _fetch_naver_foreign(ticker, pages=3)
            if fi.empty:
                foreign_5d = foreign_10d = 0
                foreign_pct = 50.0
                inst_5d = 0
            else:
                foreign_5d  = int(fi["foreign"].iloc[-5:].sum())  if len(fi) >= 5  else 0
                foreign_10d = int(fi["foreign"].iloc[-10:].sum()) if len(fi) >= 10 else 0
                inst_5d     = int(fi["inst"].iloc[-5:].sum())     if len(fi) >= 5  else 0
                # 60일 중 최근 5일 평균 외국인 순매수 분위
                mean5 = fi["foreign"].iloc[-5:].mean() if len(fi) >= 5 else 0
                ranked = (fi["foreign"] < mean5).sum() / len(fi) * 100
                foreign_pct = float(ranked)

            result[ticker] = {
                "name":               name,
                "market_cap":         mktcap,
                "close":              close_now,
                "price_5d":           round(price_5d, 2),
                "price_10d":          round(price_10d, 2),
                "vol_ratio":          round(vol_ratio, 2),
                "high52w":            high52w,
                "foreign_net_5d":     foreign_5d,
                "foreign_net_10d":    foreign_10d,
                "foreign_percentile": round(foreign_pct, 1),
                "inst_net_5d":        inst_5d,
            }
        except Exception as e:
            print(f"  [KR] {ticker} {name} 오류: {e}")
        time.sleep(0.2)

    return result


def fetch_us_data() -> dict:
    """
    US 종목 OHLCV 반환 (yfinance)
    """
    us_tickers = get_all_us_tickers()
    result = {}

    for item in us_tickers:
        ticker = item["ticker"]
        name   = item["name"]
        try:
            hist = yf.Ticker(ticker).history(period="3mo")
            if hist.empty or len(hist) < 11:
                continue
            close_now  = float(hist["Close"].iloc[-1])
            close_5d   = float(hist["Close"].iloc[-6])  if len(hist) >= 6  else close_now
            close_10d  = float(hist["Close"].iloc[-11]) if len(hist) >= 11 else close_now

            result[ticker] = {
                "name":      name,
                "close":     round(close_now, 2),
                "price_5d":  round((close_now / close_5d  - 1) * 100, 2),
                "price_10d": round((close_now / close_10d - 1) * 100, 2),
            }
        except Exception as e:
            print(f"  [US] {ticker} {name} 오류: {e}")

    return result
