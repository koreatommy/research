"""
모두의 창업 아이디어 — 통계 분석 모듈.
ideas 리스트를 받아 7개 섹션의 집계 결과를 반환한다.
"""
from __future__ import annotations

import re
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# 한국어 불용어 (키워드 추출용)
# ---------------------------------------------------------------------------
_STOPWORDS: set[str] = {
    "있는", "하는", "위한", "통한", "대한", "위해", "통해", "함께", "사용",
    "기반", "활용", "제공", "서비스", "시스템", "플랫폼", "이용", "관련",
    "모든", "가능", "다양", "새로운", "만들", "중심", "같은", "사람",
    "하여", "되는", "에서", "으로", "부터", "까지", "에게", "라는",
    "그리고", "또는", "하지", "않는", "없는", "이런", "저런", "그런",
    "것을", "것이", "것은", "수를", "등을", "들을", "들의", "들이",
    "있습니다", "합니다", "입니다", "습니다", "니다",
}

_HANGUL_WORD = re.compile(r"[가-힣]{2,}")


def _extract_keywords(texts: list[str], top_n: int = 60) -> list[dict]:
    counter: Counter[str] = Counter()
    for text in texts:
        words = _HANGUL_WORD.findall(text)
        for w in words:
            if w not in _STOPWORDS and len(w) >= 2:
                counter[w] += 1
    return [{"word": w, "count": c} for w, c in counter.most_common(top_n)]


def _parse_dt(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        raw = raw.replace("Z", "+00:00")
        return datetime.fromisoformat(raw)
    except Exception:
        return None


def _safe_div(a: float, b: float) -> float:
    return round(a / b, 2) if b else 0


def _median(values: list[int | float]) -> float:
    if not values:
        return 0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return round((s[mid - 1] + s[mid]) / 2, 2)
    return float(s[mid])


# ---------------------------------------------------------------------------
# 핵심 집계 함수
# ---------------------------------------------------------------------------

def compute_analytics(ideas: list[dict], crawled_at: str | None = None) -> dict[str, Any]:
    total = len(ideas)
    if total == 0:
        return {"meta": {"total": 0, "crawled_at": crawled_at}, "empty": True}

    # --- 기본 필드 추출 ---
    divisions = [i.get("division", "") for i in ideas]
    subcategories = [i.get("subcategory", "") for i in ideas]
    nicknames = [i.get("nickname", "") for i in ideas]
    likes_list = [i.get("likes", 0) or 0 for i in ideas]
    summaries = [i.get("summary", "") for i in ideas]
    dates_raw = [i.get("created_at") for i in ideas]
    parsed_dates = [_parse_dt(d) for d in dates_raw]

    # ===================================================================
    # Section 1 & 2: 분야 분포
    # ===================================================================
    div_counter = Counter(divisions)
    sub_counter = Counter(subcategories)

    sub_by_div: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for idea in ideas:
        d = idea.get("division", "")
        s = idea.get("subcategory", "")
        sub_by_div[d][s] += 1
    sub_by_div = {k: dict(v) for k, v in sub_by_div.items()}

    # ===================================================================
    # Section 3: 시계열
    # ===================================================================
    daily: dict[str, int] = defaultdict(int)
    weekly: dict[str, int] = defaultdict(int)
    monthly: dict[str, int] = defaultdict(int)
    weekday_counts: dict[int, int] = defaultdict(int)
    hour_counts: dict[int, int] = defaultdict(int)
    div_monthly: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for idea, dt in zip(ideas, parsed_dates):
        if dt is None:
            continue
        day_key = dt.strftime("%Y-%m-%d")
        iso_y, iso_w, _ = dt.isocalendar()
        week_key = f"{iso_y}-W{iso_w:02d}"
        month_key = dt.strftime("%Y-%m")
        daily[day_key] += 1
        weekly[week_key] += 1
        monthly[month_key] += 1
        weekday_counts[dt.weekday()] += 1
        hour_counts[dt.hour] += 1
        div_monthly[idea.get("division", "")][month_key] += 1

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_data = [{"day": weekday_names[i], "count": weekday_counts.get(i, 0)} for i in range(7)]
    hour_data = [{"hour": h, "count": hour_counts.get(h, 0)} for h in range(24)]

    all_months = sorted(set(monthly.keys()))
    div_monthly_series = {}
    for d, m_map in div_monthly.items():
        div_monthly_series[d] = [{"month": m, "count": m_map.get(m, 0)} for m in all_months]

    # ===================================================================
    # Section 4: 좋아요/참여도 분석
    # ===================================================================
    total_likes = sum(likes_list)
    avg_likes = _safe_div(total_likes, total)
    max_likes = max(likes_list) if likes_list else 0
    median_likes = _median(likes_list)

    like_ranges = [
        ("0", 0, 0),
        ("1", 1, 1),
        ("2-5", 2, 5),
        ("6-10", 6, 10),
        ("11-50", 11, 50),
        ("51+", 51, 999999),
    ]
    likes_dist = []
    for label, lo, hi in like_ranges:
        cnt = sum(1 for v in likes_list if lo <= v <= hi)
        likes_dist.append({"range": label, "count": cnt})

    top_liked = sorted(ideas, key=lambda x: x.get("likes", 0), reverse=True)[:15]
    top_liked_clean = [
        {
            "index": t.get("index"),
            "summary": t.get("summary", "")[:80],
            "division": t.get("division"),
            "subcategory": t.get("subcategory"),
            "nickname": t.get("nickname"),
            "likes": t.get("likes", 0),
            "created_at": (t.get("created_at") or "")[:10],
        }
        for t in top_liked
    ]

    likes_by_div: dict[str, dict] = {}
    div_likes: dict[str, list[int]] = defaultdict(list)
    for idea in ideas:
        div_likes[idea.get("division", "")].append(idea.get("likes", 0) or 0)
    for d, vals in div_likes.items():
        likes_by_div[d] = {
            "total": sum(vals),
            "avg": _safe_div(sum(vals), len(vals)),
            "count": len(vals),
        }

    likes_by_sub: dict[str, dict] = {}
    sub_likes: dict[str, list[int]] = defaultdict(list)
    for idea in ideas:
        sub_likes[idea.get("subcategory", "")].append(idea.get("likes", 0) or 0)
    for s, vals in sub_likes.items():
        likes_by_sub[s] = {
            "total": sum(vals),
            "avg": _safe_div(sum(vals), len(vals)),
            "count": len(vals),
        }

    # ===================================================================
    # Section 5: 참여자 분석
    # ===================================================================
    nick_counter = Counter(nicknames)
    total_contributors = len(nick_counter)
    ideas_per_contributor = _safe_div(total, total_contributors)
    single_count = sum(1 for c in nick_counter.values() if c == 1)
    single_pct = _safe_div(single_count * 100, total_contributors)
    repeat_count = total_contributors - single_count
    repeat_pct = round(100 - single_pct, 2)

    top_contributors = [
        {"nickname": n, "count": c}
        for n, c in nick_counter.most_common(15)
    ]

    contributor_by_div: dict[str, int] = {}
    for d in set(divisions):
        nicks = {i.get("nickname") for i in ideas if i.get("division") == d}
        contributor_by_div[d] = len(nicks)

    contributor_idea_dist: dict[str, int] = defaultdict(int)
    for c in nick_counter.values():
        if c == 1:
            contributor_idea_dist["1건"] += 1
        elif c <= 3:
            contributor_idea_dist["2-3건"] += 1
        elif c <= 5:
            contributor_idea_dist["4-5건"] += 1
        elif c <= 10:
            contributor_idea_dist["6-10건"] += 1
        else:
            contributor_idea_dist["11건+"] += 1

    # ===================================================================
    # Section 6: 교차 분석
    # ===================================================================
    sub_avg_likes = {
        s: info["avg"] for s, info in likes_by_sub.items()
    }

    heatmap: list[dict] = []
    for s in sorted(sub_counter.keys()):
        s_ideas = [i for i in ideas if i.get("subcategory") == s]
        month_map: dict[str, int] = defaultdict(int)
        for i in s_ideas:
            dt = _parse_dt(i.get("created_at"))
            if dt:
                month_map[dt.strftime("%Y-%m")] += 1
        for m in all_months:
            heatmap.append({"subcategory": s, "month": m, "count": month_map.get(m, 0)})

    div_like_range: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for idea in ideas:
        d = idea.get("division", "")
        lk = idea.get("likes", 0) or 0
        for label, lo, hi in like_ranges:
            if lo <= lk <= hi:
                div_like_range[d][label] += 1
                break
    div_like_range = {k: dict(v) for k, v in div_like_range.items()}

    sub_contributor_diversity: dict[str, dict] = {}
    for s in sorted(sub_counter.keys()):
        s_nicks = [i.get("nickname", "") for i in ideas if i.get("subcategory") == s]
        s_nick_counter = Counter(s_nicks)
        n_total = len(s_nicks)
        n_unique = len(s_nick_counter)
        hhi = 0.0
        if n_total > 0:
            for cnt in s_nick_counter.values():
                share = cnt / n_total
                hhi += share * share
        sub_contributor_diversity[s] = {
            "total_ideas": n_total,
            "unique_contributors": n_unique,
            "hhi": round(hhi, 4),
            "diversity_index": round(1 - hhi, 4),
        }

    hour_div: dict[str, list[dict]] = {}
    for d in sorted(set(divisions)):
        d_hours: dict[int, int] = defaultdict(int)
        for idea in ideas:
            if idea.get("division") == d:
                dt = _parse_dt(idea.get("created_at"))
                if dt:
                    d_hours[dt.hour] += 1
        hour_div[d] = [{"hour": h, "count": d_hours.get(h, 0)} for h in range(24)]

    # ===================================================================
    # Section 7: 텍스트 마이닝
    # ===================================================================
    keyword_freq = _extract_keywords(summaries, top_n=60)

    keyword_by_sub: dict[str, list[dict]] = {}
    for s in sorted(sub_counter.keys()):
        s_texts = [i.get("summary", "") for i in ideas if i.get("subcategory") == s]
        keyword_by_sub[s] = _extract_keywords(s_texts, top_n=15)

    summary_lengths = [len(s) for s in summaries]
    avg_len_by_sub: dict[str, float] = {}
    for s in sorted(sub_counter.keys()):
        s_lens = [len(i.get("summary", "")) for i in ideas if i.get("subcategory") == s]
        avg_len_by_sub[s] = _safe_div(sum(s_lens), len(s_lens))

    length_dist: dict[str, int] = defaultdict(int)
    for l in summary_lengths:
        if l < 20:
            length_dist["~20자"] += 1
        elif l < 50:
            length_dist["20~50자"] += 1
        elif l < 100:
            length_dist["50~100자"] += 1
        elif l < 200:
            length_dist["100~200자"] += 1
        else:
            length_dist["200자+"] += 1

    # ===================================================================
    # 결과 조합
    # ===================================================================
    return {
        "meta": {
            "total": total,
            "crawled_at": crawled_at,
            "division_count": len(set(divisions) - {""}),
            "subcategory_count": len(set(subcategories) - {""}),
            "total_contributors": total_contributors,
            "date_range": {
                "min": min((d for d in dates_raw if d), default=None),
                "max": max((d for d in dates_raw if d), default=None),
            },
        },
        "division_distribution": dict(div_counter),
        "subcategory_distribution": dict(sub_counter),
        "subcategory_by_division": sub_by_div,
        "time_series": {
            "daily": [{"date": k, "count": v} for k, v in sorted(daily.items())],
            "weekly": [{"week": k, "count": v} for k, v in sorted(weekly.items())],
            "monthly": [{"month": k, "count": v} for k, v in sorted(monthly.items())],
            "weekday": weekday_data,
            "hourly": hour_data,
            "division_monthly": div_monthly_series,
        },
        "likes_analysis": {
            "total_likes": total_likes,
            "avg_likes": avg_likes,
            "max_likes": max_likes,
            "median_likes": median_likes,
            "likes_distribution": likes_dist,
            "top_liked_ideas": top_liked_clean,
            "likes_by_division": likes_by_div,
            "likes_by_subcategory": likes_by_sub,
        },
        "contributor_analysis": {
            "total_contributors": total_contributors,
            "ideas_per_contributor_avg": ideas_per_contributor,
            "top_contributors": top_contributors,
            "single_idea_contributors": single_count,
            "single_idea_contributors_pct": single_pct,
            "repeat_contributors": repeat_count,
            "repeat_contributors_pct": repeat_pct,
            "contributor_by_division": contributor_by_div,
            "contributor_idea_distribution": dict(contributor_idea_dist),
        },
        "cross_analysis": {
            "subcategory_avg_likes": sub_avg_likes,
            "heatmap_data": heatmap,
            "all_months": all_months,
            "division_like_range": div_like_range,
            "subcategory_contributor_diversity": sub_contributor_diversity,
            "hour_by_division": hour_div,
        },
        "text_analysis": {
            "keyword_frequency": keyword_freq,
            "keyword_by_subcategory": keyword_by_sub,
            "avg_summary_length_by_subcategory": avg_len_by_sub,
            "summary_length_distribution": dict(length_dist),
        },
    }
