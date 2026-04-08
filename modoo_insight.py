"""
모두의 창업 아이디어 — Insight 보고서용 정량·정성·전략 분석.
summary/division/subcategory 등 텍스트·필드 기반 휴리스틱 분류.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

# ---------------------------------------------------------------------------
# 토큰·키워드
# ---------------------------------------------------------------------------
_STOPWORDS: set[str] = {
    "있는", "하는", "위한", "통한", "대한", "위해", "통해", "함께", "사용",
    "기반", "활용", "제공", "서비스", "시스템", "플랫폼", "이용", "관련",
    "모든", "가능", "다양", "새로운", "만들", "중심", "같은", "사람",
    "하여", "되는", "에서", "으로", "부터", "까지", "에게", "라는",
    "그리고", "또는", "하지", "않는", "없는", "이런", "저런", "그런",
    "것을", "것이", "것은", "수를", "등을", "들을", "들의", "들이",
    "있습니다", "합니다", "입니다", "습니다", "니다", "아이디어", "창업",
}

_HANGUL_WORD = re.compile(r"[가-힣]{2,}")

# (label, keywords) — 앞쪽이 우선 매칭
_PROBLEM_TYPES: list[tuple[str, tuple[str, ...]]] = [
    ("사회·공공·임팩트", ("환경", "탄소", "장애", "취약", "복지", "공공", "지자체", "정부", "사회문제", "기부", "임팩트", "ESG")),
    ("교육·학습", ("교육", "학습", "강의", "수업", "학생", "캠퍼스", "자격증", "시험", "튜터", "코딩교육")),
    ("유통·커머스·예약", ("배송", "쇼핑", "판매", "예약", "주문", "마켓", "유통", "매장", "결제", "구독")),
    ("건강·의료·케어", ("건강", "의료", "병원", "환자", "재활", "치료", "약", "케어", "운동", "다이어트")),
    ("생활·편의·취미", ("생활", "편리", "일상", "취미", "여가", "가정", "육아", "반려", "청소", "정리")),
    ("기술·데이터·자동화", ("AI", "인공지능", "데이터", "자동", "알고리즘", "IoT", "블록체인", "클라우드", "API", "개발")),
    ("지역·로컬·관광", ("지역", "로컬", "관광", "농촌", "전통", "축제", "마을", "상권", "동네")),
    ("금융·재테크", ("금융", "투자", "주식", "펀드", "대출", "보험", "재테크", "자산", "결제")),
    ("기타·복합", ()),
]

_CUSTOMER_SEGMENTS: list[tuple[str, tuple[str, ...]]] = [
    ("학생·청년", ("학생", "청년", "대학", "캠퍼스", "취업", "수험", "입시")),
    ("직장인", ("직장", "회사", "재택", "야근", "커리어", "퇴사")),
    ("시니어", ("시니어", "노인", "어르신", "퇴직", "요양")),
    ("주부·가정", ("주부", "육아", "맘", "가정", "자녀", "부모")),
    ("소상공인·자영업", ("소상공", "자영업", "사장", "가게", "매장", "프랜차이즈")),
    ("기업·B2B고객", ("기업", "법인", "임직원", "B2B", "도입", "사내")),
    ("농어업·생산자", ("농부", "농업", "어업", "축산", "생산자", "농가")),
    ("전체·미특정", ()),
]

_AI_KEYWORDS = (
    "ai", "AI", "인공지능", "머신러닝", "딥러닝", "gpt", "GPT", "LLM", "챗봇",
    "ChatGPT", "생성형", "자연어처리", "NLP", "비전", "이미지인식",
)

_B2B_HINTS = ("B2B", "b2b", "기업", "법인", "임직원", "도입", "사내", "공공기관", "관공서", "지자체", "정부", "학교", "병원", "납품", "ERP", "SaaS")
_B2G_HINTS = ("정부", "지자체", "공공", "행정", "국가", "공무원", "관공서", "공공기관")
_B2C_HINTS = ("소비자", "개인", "고객", "앱", "쇼핑", "예약", "배민", "일반인", "누구나")

_MOTIVATION: list[tuple[str, tuple[str, ...]]] = [
    ("사회문제·공익", ("환경", "장애", "복지", "공공", "기부", "취약", "지역사회", "봉사")),
    ("기술혁신·효율", ("자동화", "효율", "최적화", "데이터", "AI", "인공지능", "혁신")),
    ("생활불편·Pain", ("불편", "문제", "해결", "필요", "어려움", "번거")),
    ("수익·사업기회", ("수익", "매출", "창업", "사업", "프랜차이즈", "부업", "N잡")),
    ("자기실현·취미", ("취미", "열정", "관심", "좋아하는", "꿈", "도전")),
    ("기타", ()),
]

_HYPE_KEYWORDS = ("세계최초", "국내최초", "혁신적", "획기적", "완전히새로운", "완전히 새로운", "독보적", "유일무이", "게임체인저", "대박", "최고의", "완벽한")
_EXECUTION_KEYWORDS = ("프로토타입", "MVP", "시장조사", "타겟", "단가", "원가", "BM", "수익모델", "파일럿", "베타", "고객인터뷰", "PoC", "검증")

_TECH_KEYWORDS = ("AI", "인공지능", "알고리즘", "데이터", "IoT", "블록체인", "앱", "개발", "소프트웨어", "하드웨어", "기술", "자동화")
_MARKET_KEYWORDS = ("고객", "시장", "경쟁", "마케팅", "유통", "채널", "가격", "BM", "수익", "타겟", "세그먼트")

_SOCIAL_KEYWORDS = ("환경", "탄소", "장애", "취약", "복지", "기부", "지역", "공공", "봉사", "ESG", "친환경", "재활", "돌봄")


def _norm_summary(idea: dict) -> str:
    return str(idea.get("summary") or "")


def _tokens(text: str) -> set[str]:
    return {w for w in _HANGUL_WORD.findall(text) if w not in _STOPWORDS and len(w) >= 2}


def _match_first_label(text: str, rules: list[tuple[str, tuple[str, ...]]]) -> str:
    for label, kws in rules:
        if not kws:
            continue
        if any(k in text for k in kws):
            return label
    for label, kws in rules:
        if not kws:
            return label
    return "기타"


def _contains_any(text: str, kws: tuple[str, ...]) -> bool:
    return any(k in text for k in kws)


def _classify_b2x(text: str, sub: str) -> str:
    t = text
    if _contains_any(t, _B2G_HINTS):
        return "B2G"
    if _contains_any(t, _B2B_HINTS):
        return "B2B"
    if _contains_any(t, _B2C_HINTS):
        return "B2C"
    b2b_subs = {"운영관리", "네트워킹", "마케팅/PR", "프롭테크", "하드웨어", "에너지/자원", "유통/물류"}
    if sub in b2b_subs and not _contains_any(t, ("앱", "소비자", "개인", "일반")):
        return "B2B"
    return "B2C"


def _ai_used(text: str) -> bool:
    lower = text.lower()
    for k in _AI_KEYWORDS:
        if k.lower() in lower or k in text:
            return True
    return False


def _extract_keyword_frequency(texts: list[str], top_n: int = 40) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for text in texts:
        for w in _tokens(text):
            counter[w] += 1
    return [{"word": w, "count": c} for w, c in counter.most_common(top_n)]


def _union_find_cluster_count(ideas: list[dict], max_word_doc_freq: int = 400) -> dict[str, Any]:
    """공통 토큰으로 연결된 유사 그룹(클러스터) 수 — 역색인 + Union-Find."""
    n = len(ideas)
    if n == 0:
        return {"cluster_count": 0, "multi_idea_clusters": 0, "largest_cluster_size": 0, "sample_clusters": []}

    token_sets: list[set[str]] = []
    for idea in ideas:
        token_sets.append(_tokens(_norm_summary(idea)))

    word_to_indices: dict[str, list[int]] = defaultdict(list)
    for i, ts in enumerate(token_sets):
        for w in ts:
            word_to_indices[w].append(i)

    parent = list(range(n))

    def find(x: int) -> int:
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for _w, idxs in word_to_indices.items():
        m = len(idxs)
        if m < 2 or m > max_word_doc_freq:
            continue
        base = idxs[0]
        for j in idxs[1:]:
            union(base, j)

    comp_sizes: Counter[int] = Counter()
    for i in range(n):
        comp_sizes[find(i)] += 1

    multi = sum(1 for _root, sz in comp_sizes.items() if sz >= 2)
    largest = max(comp_sizes.values()) if comp_sizes else 0

    # 샘플: 규모 큰 클러스터 대표 키워드 3개
    roots_by_size = sorted(comp_sizes.items(), key=lambda x: -x[1])[:8]
    samples: list[dict[str, Any]] = []
    for root, sz in roots_by_size:
        if sz < 2:
            break
        members = [i for i in range(n) if find(i) == root]
        wc: Counter[str] = Counter()
        for i in members:
            wc.update(token_sets[i])
        top3 = [w for w, _c in wc.most_common(3)]
        samples.append({"size": sz, "top_keywords": top3})

    return {
        "cluster_count": len(comp_sizes),
        "multi_idea_clusters": multi,
        "largest_cluster_size": largest,
        "sample_clusters": samples[:5],
    }


def _score_commercialization(idea: dict) -> float:
    text = _norm_summary(idea)
    score = 0.0
    # 길이
    ln = len(text)
    if ln >= 80:
        score += 2.0
    elif ln >= 40:
        score += 1.0
    if _contains_any(text, _EXECUTION_KEYWORDS):
        score += 2.5
    if _contains_any(text, _MARKET_KEYWORDS):
        score += 1.5
    if _contains_any(text, _TECH_KEYWORDS):
        score += 0.5
    if _contains_any(text, _HYPE_KEYWORDS):
        score -= 1.0
    likes = int(idea.get("likes") or 0)
    score += min(likes, 20) * 0.05
    return round(max(0.0, score), 2)


def compute_insight(ideas: list[dict], crawled_at: str | None = None) -> dict[str, Any]:
    total = len(ideas)
    if total == 0:
        return {"meta": {"total": 0, "crawled_at": crawled_at}, "empty": True}

    summaries = [_norm_summary(i) for i in ideas]
    divisions = [str(i.get("division") or "") for i in ideas]
    subs = [str(i.get("subcategory") or "") for i in ideas]

    # 정량: 분야
    div_counter = Counter(divisions)
    sub_counter = Counter(subs)

    problem_counts: Counter[str] = Counter()
    customer_counts: Counter[str] = Counter()
    motivation_counts: Counter[str] = Counter()
    ai_yes = 0
    b2x_counts: Counter[str] = Counter()
    hype_flags = 0
    exec_flags = 0
    social_flags = 0

    tech_weak: list[dict[str, Any]] = []
    local_summaries: list[str] = []

    scores: list[float] = []
    score_by_div: dict[str, list[float]] = defaultdict(list)
    score_by_sub: dict[str, list[float]] = defaultdict(list)

    for idea, text, div, sub in zip(ideas, summaries, divisions, subs):
        problem_counts[_match_first_label(text, _PROBLEM_TYPES)] += 1
        customer_counts[_match_first_label(text, _CUSTOMER_SEGMENTS)] += 1
        motivation_counts[_match_first_label(text, _MOTIVATION)] += 1

        if _ai_used(text):
            ai_yes += 1
        b2x_counts[_classify_b2x(text, sub)] += 1

        if _contains_any(text, _HYPE_KEYWORDS):
            hype_flags += 1
        if _contains_any(text, _EXECUTION_KEYWORDS):
            exec_flags += 1
        if _contains_any(text, _SOCIAL_KEYWORDS):
            social_flags += 1

        has_tech = _contains_any(text, _TECH_KEYWORDS)
        has_mkt = _contains_any(text, _MARKET_KEYWORDS)
        if has_tech and not has_mkt and div == "일반/기술":
            tech_weak.append(
                {
                    "summary": text[:100],
                    "subcategory": sub,
                    "likes": idea.get("likes", 0),
                }
            )

        if div == "로컬":
            local_summaries.append(text)

        s = _score_commercialization(idea)
        scores.append(s)
        score_by_div[div].append(s)
        score_by_sub[sub].append(s)

    ai_no = total - ai_yes
    keyword_top = _extract_keyword_frequency(summaries, top_n=35)
    cluster_info = _union_find_cluster_count(ideas)

    # 지역 키워드
    local_kw = _extract_keyword_frequency(local_summaries, top_n=15) if local_summaries else []

    # 사회문제형 상위 키워드
    social_texts = [t for t in summaries if _contains_any(t, _SOCIAL_KEYWORDS)]
    social_kw = _extract_keyword_frequency(social_texts, top_n=20)

    # 세부분야별 평균 좋아요·건수
    likes_by_sub: dict[str, dict[str, float]] = {}
    for idea in ideas:
        sub = str(idea.get("subcategory") or "")
        lk = int(idea.get("likes") or 0)
        if sub not in likes_by_sub:
            likes_by_sub[sub] = {"sum": 0.0, "n": 0}
        likes_by_sub[sub]["sum"] += lk
        likes_by_sub[sub]["n"] += 1
    sub_stats = []
    for sub, v in likes_by_sub.items():
        n = int(v["n"])
        avg = round(v["sum"] / n, 3) if n else 0.0
        sub_stats.append({"subcategory": sub, "count": n, "avg_likes": avg, "total_likes": int(v["sum"])})

    sub_stats_sorted = sorted(sub_stats, key=lambda x: -x["count"])
    crowded = sub_stats_sorted[:5]
    sparse = sorted([x for x in sub_stats if x["count"] > 0], key=lambda x: x["count"])[:5]

    # 후속 지원: 아이디어 수 상위 분야 중 평균 좋아요 하위
    median_count = sub_stats_sorted[len(sub_stats_sorted) // 2]["count"] if sub_stats_sorted else 0
    support_candidates = [
        x for x in sub_stats
        if x["count"] >= max(10, median_count // 2) and x["avg_likes"] <= 0.15
    ]
    support_candidates = sorted(support_candidates, key=lambda x: (-x["count"], x["avg_likes"]))[:8]

    # 사업화 점수 상위 유형
    avg_score_div = {d: round(sum(score_by_div[d]) / len(score_by_div[d]), 2) for d in score_by_div}
    avg_score_sub = {s: round(sum(score_by_sub[s]) / len(score_by_sub[s]), 2) for s in score_by_sub}
    top_subs_score = sorted(
        [{"subcategory": s, "avg_score": v, "n": len(score_by_sub[s])} for s, v in avg_score_sub.items()],
        key=lambda x: -x["avg_score"],
    )[:10]

    # 과장 vs 실현 비율 (겹칠 수 있음 — 스택용으로 별도 카운트)
    only_hype = sum(1 for t in summaries if _contains_any(t, _HYPE_KEYWORDS) and not _contains_any(t, _EXECUTION_KEYWORDS))
    only_exec = sum(1 for t in summaries if _contains_any(t, _EXECUTION_KEYWORDS) and not _contains_any(t, _HYPE_KEYWORDS))
    both = sum(1 for t in summaries if _contains_any(t, _HYPE_KEYWORDS) and _contains_any(t, _EXECUTION_KEYWORDS))
    neither = total - only_hype - only_exec - both

    return {
        "meta": {"total": total, "crawled_at": crawled_at},
        "quantitative": {
            "by_division": dict(div_counter),
            "by_subcategory": dict(sub_counter),
            "problem_type": dict(problem_counts),
            "customer_segment": dict(customer_counts),
            "ai_usage": {"yes": ai_yes, "no": ai_no},
            "b2x": dict(b2x_counts),
            "top_keywords": keyword_top,
            "clusters": cluster_info,
        },
        "qualitative": {
            "motivation": dict(motivation_counts),
            "hype_vs_execution": {
                "hype_only": only_hype,
                "execution_only": only_exec,
                "both": both,
                "neither": neither,
            },
            "social_impact_keywords": social_kw,
            "social_idea_count": len(social_texts),
            "tech_weak_samples": tech_weak[:12],
            "local_top_keywords": local_kw,
            "local_idea_count": len(local_summaries),
        },
        "strategic": {
            "crowded_subcategories": crowded,
            "sparse_subcategories": sparse,
            "support_needed": support_candidates,
            "avg_commercialization_by_division": avg_score_div,
            "top_subcategories_by_commercialization_score": top_subs_score,
        },
        "scores": {
            "per_idea_sample": [
                {"index": ideas[i].get("index"), "summary": summaries[i][:80], "score": scores[i]}
                for i in sorted(range(total), key=lambda i: -scores[i])[:15]
            ],
        },
    }
