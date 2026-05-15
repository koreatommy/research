"""
모두의 창업 API 호출·복호화 공용 모듈.
crawl_modoo_all.py 및 app.py 등에서 import.

3만건+ 대량 수집을 안정적으로 처리하기 위해:
- requests.Session 연결 풀링
- 넉넉한 타임아웃(30s read, 10s connect)
- 지수 백오프 + 최대 5회 재시도
- 진행률 콜백(progress_callback) 지원
"""
from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
MAX_RETRIES = 5
RETRY_BACKOFF = 1.0


def _make_session() -> requests.Session:
    """커넥션 풀링 + 자동 재시도가 걸린 Session."""
    s = requests.Session()
    s.headers.update(HEADERS)
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


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
    retries: int = MAX_RETRIES,
    session: Optional[requests.Session] = None,
) -> tuple[Optional[list[dict]], Optional[dict]]:
    """
    지정 페이지의 아이디어 목록을 가져온다.
    session이 주어지면 연결 풀링을 활용한다.
    """
    url = f"{BASE_URL}?page={page_num}&size={page_size}&sort=createdAt%2Cdesc"
    if tag:
        url += f"&tag={requests.utils.quote(tag)}"

    for attempt in range(retries):
        try:
            if session:
                resp = session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
                resp.raise_for_status()
                raw = resp.json()
            else:
                from urllib.request import Request, urlopen
                req = Request(url, headers=HEADERS)
                with urlopen(req, timeout=READ_TIMEOUT) as r:
                    raw = json.loads(r.read())

            items = _decrypt(raw["data"], raw["timestamp"])
            return items, raw
        except Exception:
            if attempt < retries - 1:
                time.sleep(RETRY_BACKOFF * (2 ** attempt))
            else:
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


@dataclass
class CrawlProgress:
    """수집 진행 상태를 담는 데이터 클래스. app.py에서 직접 참조한다."""
    in_progress: bool = False
    current_subcategory: str = ""
    subcategory_index: int = 0
    total_subcategories: int = len(ALL_SUBCATEGORIES)
    pages_fetched: int = 0
    total_pages_estimated: int = 0
    ideas_collected: int = 0
    started_at: Optional[str] = None
    error: Optional[str] = None
    phase: str = "idle"
    subcategory_stats: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pct = 0.0
        if self.total_subcategories > 0:
            pct = round(self.subcategory_index / self.total_subcategories * 100, 1)
        return {
            "in_progress": self.in_progress,
            "phase": self.phase,
            "current_subcategory": self.current_subcategory,
            "subcategory_index": self.subcategory_index,
            "total_subcategories": self.total_subcategories,
            "percent": pct,
            "pages_fetched": self.pages_fetched,
            "total_pages_estimated": self.total_pages_estimated,
            "ideas_collected": self.ideas_collected,
            "started_at": self.started_at,
            "error": self.error,
        }


def collect_all_ideas(
    save_path: Optional[Path] = None,
    delay: float = 0.15,
    progress: Optional[CrawlProgress] = None,
) -> dict[str, Any]:
    """
    22개 세부분야별로 순회하며 아이디어를 수집한다.
    progress 객체가 주어지면 실시간으로 상태를 업데이트한다.
    """
    from datetime import datetime

    session = _make_session()

    seen_ids: set[int] = set()
    all_ideas: list[dict] = []
    global_idx = 1
    total_pages_fetched = 0
    subcategory_stats: dict[str, int] = {}

    if progress:
        progress.in_progress = True
        progress.phase = "collecting"
        progress.started_at = datetime.now().isoformat()
        progress.error = None
        progress.ideas_collected = 0
        progress.pages_fetched = 0
        progress.subcategory_index = 0

    for sub_idx, subcategory in enumerate(ALL_SUBCATEGORIES):
        if progress:
            progress.current_subcategory = subcategory
            progress.subcategory_index = sub_idx

        items0, meta0 = fetch_page(0, tag=subcategory, session=session)
        if items0 is None or meta0 is None:
            continue

        total_pages = int(meta0.get("totalPage") or 0)
        if total_pages <= 0:
            continue

        if progress:
            progress.total_pages_estimated += total_pages

        sub_count = 0
        for p in range(total_pages):
            if p == 0:
                items = items0
            else:
                items, _ = fetch_page(p, tag=subcategory, session=session)
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
            if progress:
                progress.pages_fetched = total_pages_fetched
                progress.ideas_collected = len(all_ideas)
            time.sleep(delay)

        subcategory_stats[subcategory] = sub_count
        if progress:
            progress.subcategory_stats = dict(subcategory_stats)

    if progress:
        progress.phase = "sorting"
        progress.subcategory_index = len(ALL_SUBCATEGORIES)

    all_ideas.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    for i, idea in enumerate(all_ideas, start=1):
        idea["index"] = i

    if progress:
        progress.phase = "saving"

    total_count_reported = 0
    try:
        _, first_meta = fetch_page(0, session=session)
        if first_meta:
            total_count_reported = int(first_meta.get("totalCount") or 0)
    except Exception:
        pass

    result: dict[str, Any] = {
        "crawled_at": datetime.now().isoformat(),
        "url": "https://www.modoo.or.kr/idea/list",
        "api": {
            "endpoint": BASE_URL,
            "page_size": PAGE_SIZE,
            "total_pages_fetched": total_pages_fetched,
            "total_count_reported": total_count_reported,
            "subcategory_stats": subcategory_stats,
        },
        "total": len(all_ideas),
        "ideas": all_ideas,
    }

    if save_path is not None:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    if progress:
        progress.phase = "done"
        progress.in_progress = False

    session.close()
    return result
