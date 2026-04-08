#!/usr/bin/env python3
"""
modoo_all_ideas.json → modoo_analysis.json
키워드 기반 다중 주제 분류(한 아이디어가 여러 주제에 포함될 수 있음).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_JSON = ROOT / "modoo_all_ideas.json"
OUTPUT_JSON = ROOT / "modoo_analysis.json"

# 더 구체적인 주제를 먼저 매칭 (광범위 키워드는 뒤로)
TOPIC_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("시니어/노인", ("시니어", "노인", "고령", "실버", "치매", "요양", "어르신", "독거노인", "노후")),
    ("반려동물", ("반려", "펫", "강아지", "고양이", "애완", "집사", "산책", "펫시터")),
    ("농업/농촌", ("농업", "농촌", "귀농", "귀촌", "농산물", "스마트팜", "농가", "소농")),
    ("물류/배송", ("물류", "배송", "라스트마일", "택배", "역물류", "풀필먼트")),
    ("HR/채용", ("채용", "인재", "구인", "헤드헌팅", "근로자", "급여", "계약직")),
    ("스포츠/레저", ("스포츠", "레저", "운동", "피트니스", "골프", "등산", "동호인", "체육")),
    ("법률/행정", ("법률", "법무", "행정", "소송", "변호", "등기", "인허가")),
    ("금융/핀테크", ("금융", "핀테크", "결제", "투자", "대출", "보험", "페이", "송금")),
    ("부동산/인테리어", ("부동산", "인테리어", "주거", "임대", "전세", "월세", "신혼", "집")),
    ("교육/학습", ("교육", "학습", "강의", "코칭", "튜터", "에듀", "학원", "이러닝")),
    ("헬스케어/의료", ("의료", "병원", "환자", "진단", "헬스", "재활", "치료", "건강", "간호")),
    ("환경/에너지", ("환경", "에너지", "태양광", "재활용", "탄소", "친환경", "배출", "쓰레기")),
    ("보안/안전", ("보안", "안전", "사이버", "암호", "방범", "감시", "해킹")),
    ("음식/식품", ("음식", "식품", "푸드", "레시피", "배달", "식당", "메뉴", "식재료")),
    ("여행/관광", ("여행", "관광", "숙박", "호텔", "펜션", "티켓")),
    ("엔터테인먼트", ("게임", "영상", "스트리밍", "웹툰", "웹소설", "음악", "콘텐츠", "엔터")),
    ("제조/하드웨어", ("제조", "하드웨어", "공장", "pcb", "회로", "센서", "장비")),
    ("1인가구", ("1인", "혼자 사는", "자취", "싱글", "1인가구")),
    ("패션/뷰티", ("패션", "뷰티", "화장품", "스킨케어", "의류", "메이크업")),
    ("복지/사회문제", ("복지", "장애인", "저소득", "취약계층", "사회문제", "공공")),
    ("소상공인/자영업", ("소상공인", "자영업", "사장님", "동네가게", "로컬상권")),
    ("AI/머신러닝", ("ai", "인공지능", "머신러닝", "딥러닝", "gpt", "llm", "생성형", "챗봇", "chatgpt")),
    ("플랫폼/마켓", ("플랫폼", "마켓", "마켓플레이스", "중개", "매칭", "c2c", "b2b", "b2c", "앱", "온라인몰", "쇼핑몰", "커머스")),
]

STOPWORDS = frozenset(
    "은 는 이 가 을 를 에 의 와 과 도 로 만 또 그 이거 것 수 있는 없는 위해 통해 대해 관한 위한"
    "에서 으로부터 등 및 또는 하다 되다 있다 없다 같다 이런 저런 모든 각종 해당".split()
)


def idea_text(idea: dict) -> str:
    parts = [idea.get("summary") or "", " ".join(idea.get("tags") or [])]
    return " ".join(parts).lower()


def classify_topics(text: str) -> list[str]:
    hits = []
    for name, kws in TOPIC_KEYWORDS:
        if any(kw in text for kw in kws):
            hits.append(name)
    if not hits:
        hits.append("기타")
    return hits


def tokenize_for_keywords(text: str) -> list[str]:
    raw = re.findall(r"[가-힣a-z]{2,}", text.lower())
    return [t for t in raw if t not in STOPWORDS and len(t) >= 2]


def month_key(iso_ts: str) -> str | None:
    if not iso_ts or len(iso_ts) < 7:
        return None
    try:
        return iso_ts[:7]
    except Exception:
        return None


def build_analysis(ideas: list[dict], source_crawled_at: str) -> dict:
    total = len(ideas)
    topic_assignments: dict[str, list[dict]] = defaultdict(list)
    monthly: Counter[str] = Counter()
    kw_counter: Counter[str] = Counter()
    division_counts: Counter[str] = Counter()

    for idea in ideas:
        text = idea_text(idea)
        for tok in tokenize_for_keywords(text):
            kw_counter[tok] += 1
        mk = month_key(idea.get("created_at") or "")
        if mk:
            monthly[mk] += 1
        division_counts[idea.get("division") or "기타"] += 1

        for topic in classify_topics(text):
            topic_assignments[topic].append(idea)

    topic_counts = {k: len(v) for k, v in topic_assignments.items()}
    for name, _ in TOPIC_KEYWORDS:
        topic_counts.setdefault(name, 0)
    topic_counts.setdefault("기타", 0)

    topic_stats: dict = {}
    for topic, items in topic_assignments.items():
        if not items:
            continue
        likes = [int(i.get("likes") or 0) for i in items]
        total_likes = sum(likes)
        avg = round(total_likes / len(items), 2) if items else 0.0
        top3 = sorted(items, key=lambda x: int(x.get("likes") or 0), reverse=True)[:3]
        topic_stats[topic] = {
            "count": len(items),
            "total_likes": total_likes,
            "avg_likes": avg,
            "top3": [
                {
                    "summary": t.get("summary", ""),
                    "likes": int(t.get("likes") or 0),
                    "nickname": t.get("nickname", ""),
                }
                for t in top3
            ],
        }

    for topic in topic_counts:
        topic_stats.setdefault(
            topic,
            {"count": 0, "total_likes": 0, "avg_likes": 0.0, "top3": []},
        )

    top_liked = sorted(
        ideas,
        key=lambda x: int(x.get("likes") or 0),
        reverse=True,
    )[:15]
    top_liked_out = [
        {
            "summary": i.get("summary", ""),
            "likes": int(i.get("likes") or 0),
            "nickname": i.get("nickname", ""),
            "division": i.get("division", ""),
        }
        for i in top_liked
    ]

    top_keywords = dict(kw_counter.most_common(80))

    all_likes_sum = sum(int(i.get("likes") or 0) for i in ideas)
    overall_avg_likes = round(all_likes_sum / total, 2) if total else 0.0

    tech = int(division_counts.get("일반/기술", 0))
    local = int(division_counts.get("로컬", 0))
    other_div = total - tech - local

    return {
        "generated_at": datetime.now().isoformat(),
        "source_crawled_at": source_crawled_at,
        "total": total,
        "topic_counts": dict(sorted(topic_counts.items(), key=lambda x: -x[1])),
        "topic_stats": topic_stats,
        "monthly": dict(sorted(monthly.items())),
        "top_keywords": top_keywords,
        "top_liked": top_liked_out,
        "division_counts": dict(division_counts),
        "division_tech_local": {"일반/기술": tech, "로컬": local, "기타_분류": other_div},
        "overall_avg_likes": overall_avg_likes,
    }


def main() -> None:
    if not INPUT_JSON.is_file():
        print(f"[오류] 먼저 수집 파일이 필요합니다: {INPUT_JSON}")
        print("  python crawl_modoo_all.py")
        raise SystemExit(1)

    with open(INPUT_JSON, encoding="utf-8") as f:
        raw = json.load(f)

    ideas = raw.get("ideas") or []
    if not ideas:
        print("[오류] ideas 배열이 비어 있습니다.")
        raise SystemExit(1)

    src_at = raw.get("crawled_at") or ""
    analysis = build_analysis(ideas, src_at)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"[완료] {len(ideas)}건 분석 → {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
