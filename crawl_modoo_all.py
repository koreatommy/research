#!/usr/bin/env python3
"""
모두의 창업 - 전체 아이디어 수집 CLI.
modoo_fetch 모듈의 collect_all_ideas 사용.
"""
from __future__ import annotations

import sys
from datetime import datetime

from modoo_fetch import OUTPUT_JSON, CrawlError, collect_all_ideas


def main() -> None:
    print("=" * 60)
    print("  모두의 창업 | 전체 아이디어 수집")
    print(f"  시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        result = collect_all_ideas(save_path=OUTPUT_JSON)
    except CrawlError as e:
        print(f"\n[오류] {e}", file=sys.stderr)
        return

    total = result["total"]
    api_info = result["api"]
    total_count = api_info["total_count_reported"]

    print(f"\n[완료] {total}건 수집")
    if total != total_count:
        print(
            f"  [경고] API totalCount({total_count})와 수집 건수({total})가 다릅니다. "
            "일부 페이지 요청이 실패했을 수 있습니다.",
            file=sys.stderr,
        )

    print(f"[저장] {OUTPUT_JSON.resolve()}")

    print("\n" + "=" * 60)
    print("  샘플 (처음 10건)")
    print("=" * 60)
    for d in result["ideas"][:10]:
        tags = f" [{', '.join(d['tags'])}]" if d["tags"] else ""
        print(f"\n[{d['index']:04d}] {d['division']}{tags} | 좋아요 {d['likes']} | {d['nickname']}")
        print(f"  {d['summary']}")


if __name__ == "__main__":
    main()
