"""
신호 계산 및 액션 판정
"""
from config import (
    BUY_READY, WATCH, LATE_LARGE, LATE_SMALL,
    VOLUME_RATIO_MIN, FOREIGN_PERCENTILE_MIN, HIGH52W_THRESHOLD,
    LARGE_CAP_KRW
)
from sector_pairs import SECTOR_PAIRS


def _action(kr: dict, us_peers: list, us_data: dict, kr_mktcap: int) -> dict:
    """
    단일 KR 종목 + 연결된 US 피어들로 액션 판정
    returns: {action, reason, us_best_5d, us_best_name, signal_count}
    """
    kr_5d  = kr["price_5d"]
    kr_10d = kr["price_10d"]
    close  = kr["close"]
    high52 = kr["high52w"]
    vol    = kr["vol_ratio"]
    fpct   = kr["foreign_percentile"]
    f5d    = kr["foreign_net_5d"]

    # 연결된 US 피어 중 가장 강한 것
    best_us = max(
        (us_data[p["ticker"]] for p in us_peers if p["ticker"] in us_data),
        key=lambda x: x["price_5d"],
        default=None
    )
    us_5d   = best_us["price_5d"]   if best_us else 0.0
    us_name = best_us["name"]        if best_us else "-"

    is_near_high  = close >= high52 * HIGH52W_THRESHOLD
    is_high_vol   = vol >= VOLUME_RATIO_MIN
    is_foreign_in = f5d > 0
    is_strong_foreign = fpct >= FOREIGN_PERCENTILE_MIN

    late_thresh = LATE_LARGE if kr_mktcap >= LARGE_CAP_KRW else LATE_SMALL

    # --- LATE ---
    if kr_5d >= late_thresh["kr_5d"] or kr_10d >= late_thresh["kr_10d"]:
        return dict(action="LATE", reason="이미 큰 폭 상승", us_best_5d=us_5d, us_best_name=us_name)

    # --- AVOID ---
    if us_5d <= 0 and kr_5d > 0:
        return dict(action="AVOID", reason="한국만 상승, 글로벌 동조 없음", us_best_5d=us_5d, us_best_name=us_name)
    if us_5d < 0 and kr_5d < 0:
        return dict(action="AVOID", reason="미국·한국 모두 하락", us_best_5d=us_5d, us_best_name=us_name)

    # 시차 갭: 미국이 먼저 올랐는데 한국이 아직 덜 반응
    if us_5d >= BUY_READY["us_5d_min"] and kr_5d < WATCH["kr_5d_min"]:
        return dict(action="GAP", reason=f"미국 선행 ({us_name} +{us_5d:.1f}%), 한국 미반응 → 시차 진입 기회",
                    us_best_5d=us_5d, us_best_name=us_name)

    # --- BUY READY ---
    if (us_5d >= BUY_READY["us_5d_min"]
            and kr_5d >= BUY_READY["kr_5d_min"]
            and kr_10d <= BUY_READY["kr_10d_max"]
            and is_foreign_in):
        score = sum([is_near_high, is_high_vol, is_strong_foreign])
        if score >= 2:
            return dict(action="BUY READY", reason=f"동조 상승 초입 (신호 {score}/3)", us_best_5d=us_5d, us_best_name=us_name)
        else:
            return dict(action="WATCH", reason=f"동조 시작, 수급 보강 필요 (신호 {score}/3)", us_best_5d=us_5d, us_best_name=us_name)

    # --- WATCH ---
    if (us_5d >= WATCH["us_5d_min"]
            and WATCH["kr_5d_min"] <= kr_5d <= WATCH["kr_5d_max"]):
        return dict(action="WATCH", reason="동조 초기 단계", us_best_5d=us_5d, us_best_name=us_name)

    return dict(action="AVOID", reason="조건 미충족", us_best_5d=us_5d, us_best_name=us_name)


def compute_signals(kr_data: dict, us_data: dict) -> list:
    """
    전체 종목 신호 계산
    returns: list of row dicts (대시보드 테이블용)
    """
    rows = []

    for pair in SECTOR_PAIRS:
        sector    = pair["sector"]
        us_peers  = pair["us"]
        kr_items  = pair["kr"]

        # 섹터 내 US 피어 중 상승 종목 수 (신뢰도 계산용)
        us_up_count = sum(
            1 for p in us_peers
            if p["ticker"] in us_data and us_data[p["ticker"]]["price_5d"] >= 3.0
        )
        sector_confidence = "높음" if us_up_count >= 2 else ("보통" if us_up_count == 1 else "낮음")

        for item in kr_items:
            ticker = item["ticker"]
            if ticker not in kr_data:
                continue
            kr = kr_data[ticker]
            mktcap = kr["market_cap"]

            res = _action(kr, us_peers, us_data, mktcap)

            rows.append({
                "ticker":             ticker,
                "name":               kr["name"],
                "sector":             sector,
                "market_cap_t":       round(mktcap / 1e12, 2),     # 조원
                "close":              kr["close"],
                "price_5d":           kr["price_5d"],
                "price_10d":          kr["price_10d"],
                "vol_ratio":          kr["vol_ratio"],
                "high52w":            kr["high52w"],
                "near_high":          kr["close"] >= kr["high52w"] * HIGH52W_THRESHOLD,
                "foreign_net_5d":     kr["foreign_net_5d"],
                "foreign_net_10d":    kr["foreign_net_10d"],
                "foreign_pct":        kr["foreign_percentile"],
                "us_peer":            res["us_best_name"],
                "us_5d":              res["us_best_5d"],
                "action":             res["action"],
                "reason":             res["reason"],
                "sector_confidence":  sector_confidence,
            })

    # 정렬: BUY READY → GAP → WATCH → LATE → AVOID
    order = {"BUY READY": 0, "GAP": 1, "WATCH": 2, "LATE": 3, "AVOID": 4}
    rows.sort(key=lambda x: (order.get(x["action"], 9), -x["price_5d"]))
    return rows
