"""
텔레그램 알림: 요약 텍스트 + 대시보드 링크
"""
import requests
from config import BOT_TOKEN, CHAT_ID, DASHBOARD_URL
from datetime import datetime

ACTION_ICON = {
    "BUY READY": "🟢",
    "GAP":       "⚡",
    "WATCH":     "🟡",
    "LATE":      "🔴",
    "AVOID":     "⚫",
}

def _fmt_pct(v: float) -> str:
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}%"

def build_message(rows: list) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    buy_ready = [r for r in rows if r["action"] == "BUY READY"]
    gap       = [r for r in rows if r["action"] == "GAP"]
    watch     = [r for r in rows if r["action"] == "WATCH"]
    late      = [r for r in rows if r["action"] == "LATE"]

    lines = [f"📊 *주도주 스캐너* — {today}\n"]

    if buy_ready:
        lines.append("🟢 *BUY READY*")
        for r in buy_ready:
            lines.append(
                f"  • {r['name']} ({r['sector']}) KR {_fmt_pct(r['price_5d'])} | "
                f"외국인 {r['foreign_pct']:.0f}% | {r['us_peer']} {_fmt_pct(r['us_5d'])}"
            )

    if gap:
        lines.append("\n⚡ *시차 갭 (미국 선행)*")
        for r in gap:
            lines.append(
                f"  • {r['name']} ({r['sector']}) — {r['reason']}"
            )

    if watch:
        lines.append("\n🟡 *WATCH*")
        for r in watch[:5]:  # 최대 5개
            lines.append(
                f"  • {r['name']} KR {_fmt_pct(r['price_5d'])} | {r['us_peer']} {_fmt_pct(r['us_5d'])}"
            )

    if late:
        names = ", ".join(r["name"] for r in late[:5])
        lines.append(f"\n🔴 *LATE*: {names}")

    lines.append(f"\n▶ [전체 표 보기]({DASHBOARD_URL})")
    return "\n".join(lines)


def send_telegram(rows: list):
    msg = build_message(rows)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id":    CHAT_ID,
        "text":       msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    })
    if resp.status_code == 200:
        print("[telegram] 전송 완료")
    else:
        print(f"[telegram] 오류: {resp.status_code} {resp.text}")
