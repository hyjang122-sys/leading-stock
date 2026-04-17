"""
주도주 스캐너 메인
실행: python main.py [--no-telegram] [--no-git]
"""
import argparse
import subprocess
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collector import fetch_kr_data, fetch_us_data, fetch_broad_candidates
from signals   import compute_signals, compute_momentum_signals
from dashboard import save_dashboard
from notifier  import send_telegram
from config    import BASE_DIR, DOCS_DIR

def git_push():
    try:
        subprocess.run(["git", "add", "docs/index.html"], cwd=BASE_DIR, check=True)
        msg = f"dashboard: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        print("[git] push 완료")
    except subprocess.CalledProcessError as e:
        print(f"[git] push 실패: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-telegram", action="store_true")
    parser.add_argument("--no-git",      action="store_true")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 데이터 수집 시작")
    kr_data = fetch_kr_data()
    us_data = fetch_us_data()
    print(f"  KR {len(kr_data)}종목 / US {len(us_data)}종목 수집 완료")

    rows = compute_signals(kr_data, us_data)
    print(f"  신호 계산 완료: {len(rows)}행")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 수급 스캔 시작 (중소형주 150종목)")
    candidates = fetch_broad_candidates(top_n=150)
    momentum_rows = compute_momentum_signals(candidates)
    print(f"  수급 포착: {len(momentum_rows)}종목")

    save_dashboard(rows, momentum_rows=momentum_rows)

    if not args.no_git:
        git_push()

    if not args.no_telegram:
        send_telegram(rows)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 완료")

if __name__ == "__main__":
    main()
