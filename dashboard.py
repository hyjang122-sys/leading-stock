"""
HTML 대시보드 생성 → docs/index.html
"""
import os
from datetime import datetime
from config import DOCS_DIR

ACTION_STYLE = {
    "BUY READY": ("🟢", "#1a472a", "#d4edda"),
    "GAP":       ("⚡", "#4a2c00", "#fff3cd"),
    "WATCH":     ("🟡", "#856404", "#fff8e1"),
    "LATE":      ("🔴", "#721c24", "#f8d7da"),
    "AVOID":     ("⚫", "#383838", "#f0f0f0"),
    "외인신규":   ("🔵", "#003380", "#ddeeff"),
    "외인매집":   ("🔷", "#004499", "#e8f4ff"),
    "기관매집":   ("🟣", "#4a0072", "#f3e8ff"),
}

def _fmt_pct(v: float) -> str:
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}%"

def _fmt_mktcap(t: float) -> str:
    if t >= 1:
        return f"{t:.1f}조"
    return f"{round(t*1000):.0f}억"

def _fmt_foreign(v: int) -> str:
    if abs(v) >= 1_000_000_000_000:
        return f"{v/1e12:+.1f}조"
    if abs(v) >= 100_000_000:
        return f"{v/1e8:+.0f}억"
    if abs(v) >= 10_000:
        return f"{v/1e4:+.0f}만"
    return f"{v:+,}"

def _momentum_table(momentum_rows: list) -> str:
    if not momentum_rows:
        return ""
    rows_html = ""
    for r in momentum_rows:
        icon, tc, bg = ACTION_STYLE.get(r["action"], ("", "#000", "#fff"))
        rows_html += f"""
        <tr style="background:{bg}">
          <td style="font-weight:bold;color:{tc}">{icon} {r['action']}</td>
          <td>{r['name']}<br><small style="color:#666">{r['ticker']}</small></td>
          <td style="text-align:right">{_fmt_mktcap(r['market_cap_t'])}</td>
          <td style="text-align:right;font-weight:bold">{_fmt_pct(r['price_5d'])}</td>
          <td style="text-align:right">{_fmt_foreign(r['foreign_10d'])}</td>
          <td style="text-align:right">{_fmt_foreign(r['foreign_20d'])}</td>
          <td style="text-align:right">{_fmt_foreign(r['inst_10d'])}</td>
          <td style="text-align:right">{_fmt_foreign(r['inst_20d'])}</td>
          <td style="color:#555;font-size:12px">{r['reason']}</td>
        </tr>"""
    summary_counts = {}
    for r in momentum_rows:
        summary_counts[r["action"]] = summary_counts.get(r["action"], 0) + 1
    summary_html = ""
    for action, cnt in summary_counts.items():
        icon, tc, bg = ACTION_STYLE.get(action, ("", "#000", "#fff"))
        summary_html += f'<span style="background:{bg};color:{tc};padding:4px 12px;border-radius:12px;margin:4px;font-weight:bold">{icon} {action} {cnt}</span>'
    return f"""
<h2 style="margin-top:32px;font-size:17px">📡 수급 포착 (외인·기관 매집 중소형주)</h2>
<p style="color:#888;font-size:12px;margin-bottom:8px">KOSPI+KOSDAQ 중소형주(500억~5조) 중 외국인·기관 10일 이상 순매수 종목 | 기관 = 금융투자+보험+투신+연기금 합계</p>
<div style="margin-bottom:10px">{summary_html}</div>
<table>
<thead>
<tr style="background:#343a40;color:white">
  <th>신호</th><th>종목</th><th>시총</th><th>5일%</th>
  <th>외인10일</th><th>외인20일</th><th>기관10일</th><th>기관20일</th><th>근거</th>
</tr>
</thead>
<tbody>{rows_html}</tbody>
</table>"""


def generate_html(rows: list, generated_at: str = None, momentum_rows: list = None) -> str:
    if momentum_rows is None:
        momentum_rows = []
    if not generated_at:
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    summary = {}
    for r in rows:
        summary[r["action"]] = summary.get(r["action"], 0) + 1

    summary_html = ""
    for action, cnt in sorted(summary.items(), key=lambda x: ["BUY READY","GAP","WATCH","LATE","AVOID"].index(x[0]) if x[0] in ["BUY READY","GAP","WATCH","LATE","AVOID"] else 9):
        icon, tc, bg = ACTION_STYLE.get(action, ("", "#000", "#fff"))
        summary_html += f'<span style="background:{bg};color:{tc};padding:4px 12px;border-radius:12px;margin:4px;font-weight:bold">{icon} {action} {cnt}</span>'

    rows_html = ""
    for r in rows:
        icon, tc, bg = ACTION_STYLE.get(r["action"], ("", "#000", "#fff"))
        near_high_badge = '<span style="background:#d4edda;color:#155724;padding:1px 6px;border-radius:4px;font-size:11px">신고가</span>' if r["near_high"] else ""
        high_vol_badge  = '<span style="background:#cce5ff;color:#004085;padding:1px 6px;border-radius:4px;font-size:11px">고거래량</span>' if r["vol_ratio"] >= 1.5 else ""
        rows_html += f"""
        <tr style="background:{bg}">
          <td style="font-weight:bold;color:{tc}">{icon} {r['action']}</td>
          <td>{r['name']}<br><small style="color:#666">{r['ticker']}</small></td>
          <td>{r['sector']}</td>
          <td style="text-align:right">{_fmt_mktcap(r['market_cap_t'])}</td>
          <td style="text-align:right;font-weight:bold">{_fmt_pct(r['price_5d'])}</td>
          <td style="text-align:right">{_fmt_pct(r['price_10d'])}</td>
          <td style="text-align:right">{r['vol_ratio']:.1f}x</td>
          <td>{near_high_badge}{high_vol_badge}</td>
          <td style="text-align:right">{_fmt_foreign(r['foreign_net_5d'])}</td>
          <td style="text-align:right">{_fmt_foreign(r['foreign_net_10d'])}</td>
          <td style="text-align:right">{r['foreign_pct']:.0f}%</td>
          <td>{r['us_peer']}</td>
          <td style="text-align:right">{_fmt_pct(r['us_5d'])}</td>
          <td style="color:#666;font-size:12px">{r['reason']}</td>
          <td><span style="font-size:11px">신뢰도: {r['sector_confidence']}</span></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>주도주 스캐너 — {generated_at}</title>
<style>
  body {{ font-family: -apple-system, 'Noto Sans KR', sans-serif; margin: 0; padding: 16px; background: #f8f9fa; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .updated {{ color: #888; font-size: 13px; margin-bottom: 16px; }}
  .summary {{ margin-bottom: 16px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; background: white; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
  th {{ background: #343a40; color: white; padding: 8px 10px; text-align: left; white-space: nowrap; position: sticky; top: 0; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #e0e0e0; vertical-align: middle; white-space: nowrap; }}
  tr:hover td {{ filter: brightness(0.96); }}
</style>
</head>
<body>
<h1>📊 주도주 스캐너</h1>
<div class="updated">업데이트: {generated_at} | KST</div>
<div class="summary">{summary_html}</div>
<table>
<thead>
<tr>
  <th>액션</th><th>종목</th><th>섹터</th><th>시총</th>
  <th>5일%</th><th>10일%</th><th>거래량비</th><th>신호</th>
  <th>외국인5일</th><th>외국인10일</th><th>외국인분위</th>
  <th>미국피어</th><th>미국5일%</th><th>판단근거</th><th>섹터신뢰도</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
{_momentum_table(momentum_rows)}
<p style="color:#aaa;font-size:11px;margin-top:12px">
  ※ 투자 판단은 본인 책임. 본 스캐너는 참고용입니다.
</p>
</body>
</html>"""
    return html


def save_dashboard(rows: list, momentum_rows: list = None):
    os.makedirs(DOCS_DIR, exist_ok=True)
    html = generate_html(rows, momentum_rows=momentum_rows)
    path = os.path.join(DOCS_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[dashboard] 저장 완료: {path}")
    return path
