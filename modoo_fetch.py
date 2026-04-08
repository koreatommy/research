"""
모두의 창업 API 호출·복호화 공용 모듈.
crawl_modoo_all.py 및 app.py 등에서 import.
"""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ROOT = Path(__file__).resolve().parent

BASE_URL = "https://hera-prod.modoo.or.kr/api/v1/startup-idea"
PAGE_SIZE = 12
OUTPUT_JSON = ROOT / "modoo_all_ideas.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.modoo.or.kr/idea/list",
    "Origin": "https://www.modoo.or.kr",
}

DIVISION_MAP = {
    "TECH": "일반/기술",
    "LOCAL": "로컬",
    "SOCIAL": "사회적",
    "GREEN": "그린",
    "CULTURE": "문화",
}

SUBCATEGORIES: dict[str, list[str]] = {
    "일반/기술": [
        "IT", "교육", "금융", "운영관리", "네트워킹", "농축·수산업",
        "라이프스타일", "마케팅/PR", "모빌리티", "미디어/엔터테인먼트",
        "바이오/의료", "에너지/자원", "유통/물류", "임팩트", "재무",
        "프롭테크", "하드웨어", "기타",
    ],
    "로컬": ["패션", "F&B", "뷰티", "생활"],
}

ALL_SUBCATEGORIES: list[str] = [
    sub for subs in SUBCATEGORIES.values() for sub in subs
]

SUBCATEGORY_TO_DIVISION: dict[str, str] = {
    sub: div for div, subs in SUBCATEGORIES.items() for sub in subs
}


def _decrypt(encrypted: str, timestamp: Any) -> list[dict]:
    key_str = str(timestamp).ljust(16, "0")[:16]
    key = key_str.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, key)
    raw = base64.b64decode(encrypted)
    return json.loads(unpad(cipher.decrypt(raw), AES.block_size).decode("utf-8"))


def fetch_page(
    page_num: int,
    page_size: int = PAGE_SIZE,
    tag: Optional[str] = None,
    retries: int = 3,
) -> tuple[Optional[list[dict]], Optional[dict]]:
    """
    지정 페이지의 아이디어 목록을 가져온다.
    tag가 주어지면 해당 세부분야만 필터링한다.
    Returns (items, raw_meta) 또는 (None, None) on failure.
    """
    url = f"{BASE_URL}?page={page_num}&size={page_size}&sort=createdAt%2Cdesc"
    if tag:
        url += f"&tag={quote(tag)}"
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=15) as r:
                raw = json.loads(r.read())
            items = _decrypt(raw["data"], raw["timestamp"])
            return items, raw
        except (URLError, HTTPError):
            if attempt < retries - 1:
                time.sleep(2**attempt)
            else:
                return None, None
        except Exception:
            return None, None
    return None, None


def parse_item(item: dict, idx: int, subcategory: Optional[str] = None) -> dict:
    """원시 API 아이템을 정규화된 dict로 변환."""
    applicant = item.get("applicant") or {}
    division_raw = item.get("division", "")
    division = DIVISION_MAP.get(division_raw, division_raw)
    return {
        "index": idx,
        "id": item.get("id"),
        "summary": item.get("summary", ""),
        "division": division,
        "subcategory": subcategory,
        "nickname": applicant.get("nickname", ""),
        "likes": item.get("likeCount", 0),
        "is_public": item.get("isPublic", False),
        "tags": [t.get("name", "") for t in (item.get("tags") or [])],
        "created_at": item.get("createdAt", ""),
    }


class CrawlError(Exception):
    """수집 중 오류 발생 시 raise."""


def collect_all_ideas(
    save_path: Optional[Path] = None,
    delay: float = 0.25,
) -> dict[str, Any]:
    """
    22개 세부분야별로 순회하며 아이디어를 수집한다.
    save_path가 주어지면 해당 경로에 JSON도 저장한다.

    Returns:
        {
            "crawled_at": str (ISO),
            "url": str,
            "api": {...},
            "total": int,
            "ideas": list[dict],
        }

    Raises:
        CrawlError: 페이지 요청 실패 시.
    """
    from datetime import datetime

    seen_ids: set[int] = set()
    all_ideas: list[dict] = []
    global_idx = 1
    total_pages_fetched = 0
    subcategory_stats: dict[str, int] = {}

    for subcategory in ALL_SUBCATEGORIES:
        items0, meta0 = fetch_page(0, tag=subcategory)
        if items0 is None or meta0 is None:
            continue

        total_pages = int(meta0.get("totalPage") or 0)
        if total_pages <= 0:
            continue

        sub_count = 0
        for p in range(total_pages):
            if p == 0:
                items = items0
            else:
                items, _ = fetch_page(p, tag=subcategory)
                if items is None:
                    break
                time.sleep(delay)

            for item in items:
                idea_id = item.get("id")
                if idea_id in seen_ids:
                    continue
                seen_ids.add(idea_id)
                all_ideas.append(parse_item(item, global_idx, subcategory))
                global_idx += 1
                sub_count += 1

            total_pages_fetched += 1
            time.sleep(delay)

        subcategory_stats[subcategory] = sub_count

    all_ideas.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    for i, idea in enumerate(all_ideas, start=1):
        idea["index"] = i

    result: dict[str, Any] = {
        "crawled_at": datetime.now().isoformat(),
        "url": "https://www.modoo.or.kr/idea/list",
        "api": {
            "endpoint": BASE_URL,
            "page_size": PAGE_SIZE,
            "total_pages_fetched": total_pages_fetched,
            "subcategory_stats": subcategory_stats,
        },
        "total": len(all_ideas),
        "ideas": all_ideas,
    }

    if save_path is not None:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return result
