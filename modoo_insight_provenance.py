"""
인사이트(/insight) 데이터 출처·전수 스냅샷 메타데이터.
동일 전수를 기준으로 insight를 재계산·외부 분석할 때 참조용 JSON을 만든다.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modoo_fetch import ALL_SUBCATEGORIES, BASE_URL, PAGE_SIZE


def _sorted_id_fingerprint(ideas: list[dict]) -> str:
    ids = sorted({i.get("id") for i in ideas if i.get("id") is not None})
    raw = json.dumps(ids, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_insight_data_source(
    bundle: dict[str, Any],
    *,
    repo_relative_primary_json: str = "modoo_all_ideas.json",
    research_export_dir: str = "research/data",
) -> dict[str, Any]:
    """
    modoo_all_ideas.json (또는 동일 스키마 dict)로부터 출처·전수 정보를 구성한다.

    bundle 키: crawled_at, url, api, total, ideas (collect_all_ideas / 로드 결과와 동일)
    """
    ideas: list[dict] = bundle.get("ideas") or []
    n = len(ideas)
    declared = int(bundle.get("total") or 0)
    api_block = bundle.get("api") if isinstance(bundle.get("api"), dict) else {}

    from modoo_insight import compute_insight

    insight = compute_insight(ideas, crawled_at=bundle.get("crawled_at"))
    meta = insight.get("meta") or {}
    insight_meta_total: int | None = meta["total"] if isinstance(meta.get("total"), int) else None

    consistency = {
        "ideas_len_equals_declared_total": n == declared if declared else None,
        "ideas_len_equals_insight_meta_total": n == insight_meta_total if insight_meta_total is not None else None,
    }

    return {
        "schema_version": "1.0",
        "document_type": "insight_data_source",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose_ko": (
            "인사이트 화면 및 insight.json의 근거가 된 전수(스냅샷) 데이터 출처·범위·"
            "재현에 필요한 메타데이터. 외부 도구로 전수 재분석 시 입력 파일·건수·수집 시각을 식별한다."
        ),
        "full_census": {
            "definition_ko": (
                "본 JSON에서 전수는 '수집 시점에 중복 제거된 ideas 배열의 모든 행'을 의미한다. "
                "인사이트 집계(분야별 건수, AI 비율 등)는 이 배열 전체를 순회해 계산된다."
            ),
            "row_count": n,
            "declared_total_field": declared,
            "distinct_idea_ids": len({i.get("id") for i in ideas if i.get("id") is not None}),
            "idea_id_sorted_sha256": _sorted_id_fingerprint(ideas),
        },
        "primary_dataset": {
            "role": "insight_and_analytics_source_of_truth",
            "repository_relative_path": repo_relative_primary_json,
            "mirror_after_export_relative_path": f"{research_export_dir}/ideas.json",
            "crawled_at": bundle.get("crawled_at"),
            "list_page_url": bundle.get("url"),
        },
        "collection": {
            "method_ko": (
                "세부분야(서브카테고리)별로 API totalPage만큼 페이지를 순회해 수집. "
                "동일 id는 한 번만 유지(전역 중복 제거)."
            ),
            "api_endpoint": api_block.get("endpoint") or BASE_URL,
            "page_size": api_block.get("page_size") or PAGE_SIZE,
            "total_pages_fetched": api_block.get("total_pages_fetched"),
            "subcategory_stats": api_block.get("subcategory_stats"),
            "subcategories_enumerated": list(ALL_SUBCATEGORIES),
            "subcategory_count": len(ALL_SUBCATEGORIES),
        },
        "derived_artifacts": {
            "insight_json_relative": f"{research_export_dir}/insight.json",
            "analytics_json_relative": f"{research_export_dir}/analytics.json",
            "this_file_relative": f"{research_export_dir}/insight_data_source.json",
        },
        "insight_pipeline": {
            "implementation": "modoo_insight.compute_insight",
            "input_scope_ko": "ideas 리스트 전체(페이지 분할 없이 동일 배열을 그대로 전달)",
            "runtime_api_path": "/api/insight",
            "static_export_note_ko": (
                "정적 호스팅 시 /data/insight.json 이 있으면 프론트가 우선 사용; "
                "로컬 서버에서는 크롤 후 insight_data_source.json이 함께 갱신된다."
            ),
            "algorithmic_limits_ko": (
                "클러스터링(유사 그룹 수): 매우 흔한 단어(문서 출현 수 > max_word_doc_freq=400)는 "
                "아이디어 간 연결에 사용하지 않음. 키워드 상위 N·샘플 목록 등은 표시용 truncation."
            ),
        },
        "consistency_checks": consistency,
    }


def write_insight_data_source(path: str | Path, bundle: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """빌드 후 UTF-8 JSON으로 저장. 저장한 dict를 반환."""

    p = Path(path)
    doc = build_insight_data_source(bundle, **kwargs)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return doc
