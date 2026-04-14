#!/usr/bin/env python3
"""
modoo_all_ideas.json을 Vercel용 research 레포의 data/로보냅니다.
  - ideas.json: 원본과 동일 내용(복사)
  - analytics.json: modoo_analytics.compute_analytics 결과
  - insight.json: modoo_insight.compute_insight 결과
  - insight_data_source.json: 인사이트 전수 출처·재현 메타데이터

사용 예:
  python3 export_for_research.py
  python3 export_for_research.py --out /path/to/research/data
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "modoo_all_ideas.json"
DEFAULT_OUT = ROOT / "research" / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export ideas + analytics for static research site.")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="입력 JSON (기본: modoo_all_ideas.json)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="출력 디렉터리 (기본: research/data)",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f"소스 파일이 없습니다: {args.source}")

    args.out.mkdir(parents=True, exist_ok=True)
    dest_ideas = args.out / "ideas.json"
    shutil.copyfile(args.source, dest_ideas)

    with open(args.source, encoding="utf-8") as f:
        data = json.load(f)
    ideas = data.get("ideas") or []
    crawled_at = data.get("crawled_at")

    from modoo_analytics import compute_analytics
    from modoo_insight import compute_insight
    from modoo_insight_provenance import write_insight_data_source

    analytics = compute_analytics(ideas, crawled_at=crawled_at)
    dest_analytics = args.out / "analytics.json"
    with open(dest_analytics, "w", encoding="utf-8") as f:
        json.dump(analytics, f, ensure_ascii=False, indent=2)

    insight = compute_insight(ideas, crawled_at=crawled_at)
    dest_insight = args.out / "insight.json"
    with open(dest_insight, "w", encoding="utf-8") as f:
        json.dump(insight, f, ensure_ascii=False, indent=2)

    dest_source = args.out / "insight_data_source.json"
    write_insight_data_source(dest_source, data)

    print(f"Wrote {dest_ideas}")
    print(f"Wrote {dest_analytics}")
    print(f"Wrote {dest_insight}")
    print(f"Wrote {dest_source}")


if __name__ == "__main__":
    main()
