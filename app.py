"""
모두의 창업 아이디어 로컬 뷰어 - FastAPI 서버.
uvicorn app:app --reload --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import asyncio
import json
import math
import re
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from modoo_fetch import CrawlError, collect_all_ideas
from modoo_filters import TECH_SUBCATEGORIES, LOCAL_SUBCATEGORIES, filter_ideas
from modoo_analytics import compute_analytics
from modoo_insight import compute_insight

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "modoo_all_ideas.json"
RESEARCH_DIR = ROOT / "research"
STATIC_DIR = RESEARCH_DIR / "static"
DATA_DIR = RESEARCH_DIR / "data"

ideas_data: dict[str, Any] = {}
crawl_lock = asyncio.Lock()

# openpyxl이 거부하는 제어 문자(예: U+0000) 제거 — API 원문에 포함될 수 있음
_ILLEGAL_XLSX_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _xlsx_cell_str(value: Any) -> Any:
    if isinstance(value, str):
        return _ILLEGAL_XLSX_CHARS.sub("", value)
    return value


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ideas_data
    if JSON_PATH.is_file():
        with open(JSON_PATH, encoding="utf-8") as f:
            ideas_data = json.load(f)
    else:
        ideas_data = {"ideas": [], "total": 0, "crawled_at": None, "url": None}
    yield


app = FastAPI(title="모두의 창업 뷰어", lifespan=lifespan)

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if DATA_DIR.is_dir():
    app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")


@app.get("/")
async def index():
    html_path = RESEARCH_DIR / "index.html"
    if html_path.is_file():
        return FileResponse(html_path, media_type="text/html")
    return {"message": "research/index.html 파일이 없습니다."}


@app.get("/api/meta")
async def api_meta():
    total = ideas_data.get("total", 0)
    crawled_at = ideas_data.get("crawled_at")
    source_url = ideas_data.get("url")
    api_info = ideas_data.get("api")
    ideas: list = ideas_data.get("ideas") or []

    divisions = sorted({str(i.get("division") or "") for i in ideas if i.get("division")})

    subcategories_by_division: dict[str, list[str]] = {}
    for idea in ideas:
        div = idea.get("division")
        sub = idea.get("subcategory")
        if div and sub:
            if div not in subcategories_by_division:
                subcategories_by_division[div] = []
            if sub not in subcategories_by_division[div]:
                subcategories_by_division[div].append(sub)

    if not subcategories_by_division:
        subcategories_by_division = {
            "일반/기술": list(TECH_SUBCATEGORIES),
            "로컬": list(LOCAL_SUBCATEGORIES),
        }

    return {
        "total": total,
        "crawled_at": crawled_at,
        "source_url": source_url,
        "api": api_info,
        "message": None if total else "데이터가 없습니다. '최신 데이터 수집' 버튼을 눌러주세요.",
        "divisions": divisions,
        "subcategories": subcategories_by_division,
    }


@app.get("/api/ideas")
async def api_ideas(
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page"),
    division: Optional[str] = Query(None, description="대분야 (일반/기술, 로컬 등)"),
    subcategory: Optional[str] = Query(None, description="세부분야 (분야정리.md 기준)"),
    q: Optional[str] = Query(None, description="아이디어 요약·태그 포함 검색"),
):
    ideas: list[dict] = ideas_data.get("ideas") or []
    raw_total = len(ideas)

    div_param = division.strip() if division and division.strip() else None
    sub_param = subcategory.strip() if subcategory and subcategory.strip() else None
    q_param = q.strip() if q and q.strip() else None

    filtered = filter_ideas(
        ideas,
        division=div_param,
        subcategory=sub_param,
        q=q_param,
    )
    total = len(filtered)
    total_pages = max(1, math.ceil(total / page_size)) if total else 1
    page = min(page, total_pages)

    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "raw_total": raw_total,
        "filters": {
            "division": div_param,
            "subcategory": sub_param,
            "q": q_param,
        },
    }


@app.post("/api/crawl")
async def api_crawl():
    """최신 데이터 수집. 동시 요청 방지."""
    global ideas_data

    if crawl_lock.locked():
        raise HTTPException(status_code=409, detail="수집이 이미 진행 중입니다")

    async with crawl_lock:
        try:
            result = await asyncio.to_thread(collect_all_ideas, JSON_PATH)
        except CrawlError as e:
            raise HTTPException(status_code=500, detail=str(e))

        ideas_data = result

    return {
        "ok": True,
        "total": result["total"],
        "crawled_at": result["crawled_at"],
        "message": f"{result['total']}건 수집 완료",
    }


@app.get("/analytics")
async def analytics_page():
    html_path = RESEARCH_DIR / "analytics.html"
    if html_path.is_file():
        return FileResponse(html_path, media_type="text/html")
    return {"message": "research/analytics.html 파일이 없습니다."}


@app.get("/insight")
async def insight_page():
    html_path = RESEARCH_DIR / "insight.html"
    if html_path.is_file():
        return FileResponse(html_path, media_type="text/html")
    return {"message": "research/insight.html 파일이 없습니다."}


@app.get("/api/analytics")
async def api_analytics():
    ideas: list = ideas_data.get("ideas") or []
    crawled_at = ideas_data.get("crawled_at")
    return compute_analytics(ideas, crawled_at=crawled_at)


@app.get("/api/insight")
async def api_insight():
    ideas: list = ideas_data.get("ideas") or []
    crawled_at = ideas_data.get("crawled_at")
    return compute_insight(ideas, crawled_at=crawled_at)


@app.get("/api/export/json")
async def api_export_json():
    """현재 데이터를 JSON 파일로 다운로드."""
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"modoo_ideas_{date_str}.json"

    content = json.dumps(ideas_data, ensure_ascii=False, indent=2)
    return Response(
        content=content.encode("utf-8"),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/xlsx")
async def api_export_xlsx():
    """현재 데이터를 엑셀 파일로 다운로드."""
    try:
        from openpyxl import Workbook
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl 패키지가 설치되지 않았습니다")

    wb = Workbook()
    ws = wb.active
    ws.title = "아이디어"

    headers = ["번호", "아이디어", "분야", "세부분야", "도전자", "좋아요", "등록일", "태그", "ID"]
    ws.append(headers)

    for idea in ideas_data.get("ideas") or []:
        tags_joined = ", ".join(
            _xlsx_cell_str(t) if isinstance(t, str) else str(t)
            for t in (idea.get("tags") or [])
        )
        ws.append([
            idea.get("index", ""),
            _xlsx_cell_str(idea.get("summary", "")),
            _xlsx_cell_str(idea.get("division", "")),
            _xlsx_cell_str(idea.get("subcategory", "")),
            _xlsx_cell_str(idea.get("nickname", "")),
            idea.get("likes", 0),
            _xlsx_cell_str((idea.get("created_at") or "")[:10]),
            tags_joined,
            _xlsx_cell_str(idea.get("id", "")) if idea.get("id") is not None else "",
        ])

    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                cell_len = len(str(cell.value)) if cell.value else 0
                if cell_len > max_len:
                    max_len = cell_len
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 2, 60)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"modoo_ideas_{date_str}.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
