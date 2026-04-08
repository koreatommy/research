"""
세부분야 필터링 모듈.
크롤링 시 subcategory 필드가 저장되므로 직접 비교한다.
"""
from __future__ import annotations

from typing import Iterable, Optional

from modoo_fetch import SUBCATEGORIES, SUBCATEGORY_TO_DIVISION

TECH_SUBCATEGORIES: tuple[str, ...] = tuple(SUBCATEGORIES.get("일반/기술", []))
LOCAL_SUBCATEGORIES: tuple[str, ...] = tuple(SUBCATEGORIES.get("로컬", []))


def _idea_text(idea: dict) -> str:
    summary = (idea.get("summary") or "").lower()
    tags = idea.get("tags") or []
    tag_part = " ".join(str(t).lower() for t in tags)
    return f"{summary} {tag_part}"


def idea_passes_filters(
    idea: dict,
    *,
    division: Optional[str],
    subcategory: Optional[str],
    q: Optional[str],
) -> bool:
    div = idea.get("division") or ""

    if division and div != division:
        return False

    if q:
        needle = q.strip().lower()
        if needle and needle not in _idea_text(idea):
            return False

    if subcategory:
        idea_sub = idea.get("subcategory") or ""
        if idea_sub != subcategory:
            return False

    return True


def filter_ideas(
    ideas: Iterable[dict],
    *,
    division: Optional[str],
    subcategory: Optional[str],
    q: Optional[str],
) -> list[dict]:
    return [
        i for i in ideas
        if idea_passes_filters(i, division=division, subcategory=subcategory, q=q)
    ]
