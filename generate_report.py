#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANALYSIS_PATH = ROOT / "modoo_analysis.json"
ALL_IDEAS_PATH = ROOT / "modoo_all_ideas.json"
REPORT_PATH = ROOT / "modoo_report.html"


def _division_from_ideas() -> tuple[int, int]:
    with open(ALL_IDEAS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    tech = loc = 0
    for i in raw.get("ideas") or []:
        d = i.get("division") or ""
        if d == "일반/기술":
            tech += 1
        elif d == "로컬":
            loc += 1
    return tech, loc


with open(ANALYSIS_PATH, encoding="utf-8") as f:
    analysis = json.load(f)

if (
    not analysis.get("source_crawled_at")
    and not analysis.get("generated_at")
    and ALL_IDEAS_PATH.is_file()
):
    with open(ALL_IDEAS_PATH, encoding="utf-8") as f:
        _raw_meta = json.load(f)
    analysis["source_crawled_at"] = _raw_meta.get("crawled_at", "")

tc = analysis["topic_counts"]
ts = analysis["topic_stats"]
keywords = analysis["top_keywords"]
top_liked = analysis["top_liked"]
total = analysis["total"]

div_tl = analysis.get("division_tech_local")
if div_tl and isinstance(div_tl, dict) and "일반/기술" in div_tl:
    div_tech = int(div_tl["일반/기술"])
    div_local = int(div_tl["로컬"])
elif ALL_IDEAS_PATH.is_file():
    div_tech, div_local = _division_from_ideas()
else:
    div_tech, div_local = 0, 0

div_sum = div_tech + div_local
pct_tech = round(100 * div_tech / div_sum, 1) if div_sum else 0.0
pct_loc = round(100 * div_local / div_sum, 1) if div_sum else 0.0

max_tc = max(tc.values()) if tc else 1
n_topics = len(tc)

top_topic_name, top_topic_count = max(tc.items(), key=lambda x: x[1])
top_topic_pct = round(100 * top_topic_count / total, 1) if total else 0.0

ai_kw_hits = int(keywords.get("ai", 0))

if top_liked:
    max_like = int(top_liked[0]["likes"])
    s0 = top_liked[0]["summary"]
    max_like_blurb = (s0[:40] + "…") if len(s0) > 40 else s0
else:
    max_like, max_like_blurb = 0, "-"

kw_sorted = sorted(keywords.items(), key=lambda x: -x[1])
if kw_sorted:
    top_kw_label, top_kw_count = kw_sorted[0]
    top_kw_big = top_kw_label.upper() if len(top_kw_label) <= 4 else top_kw_label
else:
    top_kw_label, top_kw_count, top_kw_big = "-", 0, "-"
top_kw_pct = round(100 * top_kw_count / total, 1) if total else 0.0

overall_avg = analysis.get("overall_avg_likes")
if overall_avg is None and ALL_IDEAS_PATH.is_file():
    with open(ALL_IDEAS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    ids = raw.get("ideas") or []
    overall_avg = round(
        sum(int(i.get("likes") or 0) for i in ids) / len(ids), 2
    ) if ids else 0.0
elif overall_avg is None:
    overall_avg = 0.0

cand_avg = [(k, v) for k, v in ts.items() if v.get("count", 0) >= 5]
if cand_avg:
    best_topic_name, best_stat = max(cand_avg, key=lambda x: x[1].get("avg_likes", 0))
    best_topic_avg = best_stat["avg_likes"]
else:
    best_topic_name, best_topic_avg = "-", 0.0

comp_topics = [(k, v) for k, v in tc.items() if k != "기타" and v > 0]
if comp_topics:
    rare_topic_name, rare_topic_cnt = min(comp_topics, key=lambda x: x[1])
    rare_topic_avg = ts[rare_topic_name]["avg_likes"]
else:
    rare_topic_name, rare_topic_cnt, rare_topic_avg = "-", 0, 0.0

ai_class_cnt = int(tc.get("AI/머신러닝", 0))
ai_class_pct = round(100 * ai_class_cnt / total, 1) if total else 0.0
sn = ts.get("시니어/노인", {})
senior_cnt = int(sn.get("count", 0))
senior_avg = float(sn.get("avg_likes", 0))
senior_pct = round(100 * senior_cnt / total, 1) if total else 0.0
sp = ts.get("스포츠/레저", {})
sp_cnt, sp_avg = int(sp.get("count", 0)), float(sp.get("avg_likes", 0))
sp_pct = round(100 * sp_cnt / total, 1) if total else 0.0
hr_cnt = int(ts.get("HR/채용", {}).get("count", 0))
log_cnt = int(ts.get("물류/배송", {}).get("count", 0))
farm_cnt = int(ts.get("농업/농촌", {}).get("count", 0))
welfare_cnt = int(ts.get("복지/사회문제", {}).get("count", 0))
env_cnt = int(ts.get("환경/에너지", {}).get("count", 0))
hr_avg = float(ts.get("HR/채용", {}).get("avg_likes", 0))
kw_global = int(keywords.get("글로벌", 0))
kw_korea = int(keywords.get("한국", 0))
kw_foreign = int(keywords.get("외국인", 0))

src_date = analysis.get("source_crawled_at") or analysis.get("generated_at") or ""
hero_date = src_date[:10].replace("-", ".") if len(src_date) >= 10 else "-"

topics_sorted = sorted(tc.items(), key=lambda x: x[1], reverse=True)
topic_labels = [t[0] for t in topics_sorted]
topic_values = [t[1] for t in topics_sorted]
topic_avg_likes = [ts[t[0]]["avg_likes"] for t in topics_sorted]

kw_items = list(keywords.items())[:40]
kw_labels = [k[0] for k in kw_items]
kw_values = [k[1] for k in kw_items]

top_liked_rows = ""
for i, item in enumerate(top_liked):
    summary = item["summary"][:88] + ("..." if len(item["summary"]) > 88 else "")
    div = item["division"]
    badge_cls = "badge-blue" if div == "일반/기술" else "badge-green"
    top_liked_rows += f"""<tr>
      <td style="font-weight:700;color:#3B5BDB">{i+1}</td>
      <td>{summary}</td>
      <td><span class="badge {badge_cls}">{div}</span></td>
      <td>{item['nickname']}</td>
      <td style="font-weight:700;color:#F03E3E">♥ {item['likes']}</td>
    </tr>\n"""

detail_rows = ""
for t in topic_labels:
    count = ts[t]["count"]
    avg = ts[t]["avg_likes"]
    total_lk = ts[t]["total_likes"]
    pct = min(count / max_tc * 100, 100) if max_tc else 0
    if avg >= 3:
        color = "#F03E3E"
    elif avg >= 2.5:
        color = "#E67700"
    else:
        color = "#868E96"
    top_idea = ts[t]['top3'][0]['summary'][:55] + "..." if ts[t]['top3'] and len(ts[t]['top3'][0]['summary']) > 55 else (ts[t]['top3'][0]['summary'] if ts[t]['top3'] else "-")
    detail_rows += f"""<tr>
      <td><strong>{t}</strong></td>
      <td>{count}건</td>
      <td><div style="background:#eee;border-radius:4px;overflow:hidden;width:80px;height:8px;"><div style="background:#3B5BDB;width:{pct:.0f}%;height:100%;"></div></div></td>
      <td><span style="color:{color};font-weight:700;">♥ {avg}</span></td>
      <td>{total_lk}개</td>
      <td style="font-size:0.83rem;color:#495057">{top_idea}</td>
    </tr>\n"""

# 매트릭스 데이터
matrix_data_list = []
for t in tc:
    if t != "기타":
        matrix_data_list.append({"x": ts[t]["count"], "y": ts[t]["avg_likes"], "label": t})

html = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>모두의 창업 아이디어 분석 보고서</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
:root {
  --primary: #3B5BDB; --secondary: #7048E8; --accent: #F03E3E;
  --success: #2F9E44; --warning: #E67700; --bg: #F8F9FA;
  --card: #FFFFFF; --text: #212529; --muted: #868E96; --border: #DEE2E6;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Apple SD Gothic Neo','Pretendard',-apple-system,BlinkMacSystemFont,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }
.hero { background:linear-gradient(135deg,#3B5BDB 0%,#7048E8 100%); color:white; padding:60px 40px; text-align:center; }
.hero h1 { font-size:2.4rem; font-weight:800; margin-bottom:12px; letter-spacing:-0.5px; }
.hero p { font-size:1.1rem; opacity:0.85; margin-bottom:24px; }
.hero-meta { display:flex; justify-content:center; gap:40px; flex-wrap:wrap; }
.hero-stat { background:rgba(255,255,255,0.15); border-radius:12px; padding:16px 28px; }
.hero-stat .num { font-size:2rem; font-weight:700; }
.hero-stat .lbl { font-size:0.85rem; opacity:0.8; margin-top:4px; }
.container { max-width:1200px; margin:0 auto; padding:40px 24px; }
.section { margin-bottom:52px; }
.section-title { font-size:1.4rem; font-weight:700; color:var(--primary); border-left:4px solid var(--primary); padding-left:14px; margin-bottom:24px; }
.section-sub { font-size:0.95rem; color:var(--muted); margin-top:-16px; margin-bottom:20px; margin-left:18px; }
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:24px; }
.grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.grid-4opp { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
@media(max-width:768px) { .grid-2,.grid-3,.grid-4opp { grid-template-columns:1fr; } }
.card { background:var(--card); border-radius:16px; padding:24px; box-shadow:0 2px 12px rgba(0,0,0,0.07); }
.card h3 { font-size:1rem; color:var(--muted); margin-bottom:8px; font-weight:500; }
.card .big { font-size:2.2rem; font-weight:800; color:var(--text); }
.card .sub { font-size:0.85rem; color:var(--muted); margin-top:4px; }
.chart-wrap { background:var(--card); border-radius:16px; padding:28px; box-shadow:0 2px 12px rgba(0,0,0,0.07); }
.chart-title { font-size:1rem; font-weight:600; color:var(--text); margin-bottom:20px; }
table { width:100%; border-collapse:collapse; }
th { background:#EDF2FF; color:var(--primary); font-size:0.85rem; padding:10px 14px; text-align:left; border-bottom:2px solid var(--primary); }
td { padding:10px 14px; font-size:0.9rem; border-bottom:1px solid var(--border); vertical-align:top; }
tr:hover td { background:#F8F9FA; }
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-blue { background:#DBE4FF; color:#3B5BDB; }
.badge-green { background:#D3F9D8; color:#2F9E44; }
.badge-orange { background:#FFE8CC; color:#E67700; }
.badge-red { background:#FFE3E3; color:#F03E3E; }
.badge-purple { background:#EDE9FE; color:#7048E8; }
.insight-box { border-radius:16px; padding:24px; margin-bottom:16px; border-left:5px solid; }
.insight-blue { background:#EDF2FF; border-color:var(--primary); }
.insight-green { background:#EBFBEE; border-color:var(--success); }
.insight-orange { background:#FFF4E6; border-color:var(--warning); }
.insight-red { background:#FFF5F5; border-color:var(--accent); }
.insight-purple { background:#F3F0FF; border-color:var(--secondary); }
.insight-box h4 { font-size:1.05rem; font-weight:700; margin-bottom:8px; }
.insight-box p { font-size:0.9rem; line-height:1.7; }
.opp-card { background:var(--card); border-radius:16px; padding:24px; box-shadow:0 2px 12px rgba(0,0,0,0.07); border-top:4px solid; position:relative; }
.opp-card .rank { position:absolute; top:20px; right:20px; font-size:1.8rem; font-weight:900; opacity:0.1; }
.opp-card h4 { font-size:1.1rem; font-weight:700; margin-bottom:8px; }
.opp-card .why { font-size:0.88rem; color:var(--muted); margin-top:10px; line-height:1.6; }
.opp-card .meta { display:flex; gap:12px; flex-wrap:wrap; margin-top:12px; }
.opp-card .meta span { font-size:0.82rem; padding:4px 10px; border-radius:20px; }
.keyword-cloud { display:flex; flex-wrap:wrap; gap:10px; padding:8px 0; }
.kw-item { padding:6px 14px; border-radius:20px; font-size:0.85rem; font-weight:600; background:linear-gradient(135deg,#DBE4FF,#E0C3FC); color:#3B5BDB; }
.kw-large { font-size:1.15rem; padding:8px 18px; background:linear-gradient(135deg,#3B5BDB,#7048E8); color:white; }
.kw-medium { font-size:1rem; padding:7px 16px; }
.kw-small { font-size:0.82rem; padding:5px 12px; opacity:0.75; }
footer { background:#212529; color:#ADB5BD; text-align:center; padding:32px; font-size:0.85rem; margin-top:40px; }
</style>
</head>
<body>

<div class="hero">
  <h1>&#x1F680; 모두의 창업 아이디어 분석 보고서</h1>
  <p>modoo.or.kr 전체 공개 아이디어 데이터 기반 심층 분석</p>
  <div class="hero-meta">
    <div class="hero-stat"><div class="num">@@TOTAL_CASES@@</div><div class="lbl">총 수집 아이디어</div></div>
    <div class="hero-stat"><div class="num">@@N_TOPICS@@</div><div class="lbl">주제 분류</div></div>
    <div class="hero-stat"><div class="num">@@AI_KW_HITS@@</div><div class="lbl">AI 키워드 언급</div></div>
    <div class="hero-stat"><div class="num">@@HERO_DATE@@</div><div class="lbl">수집 일자</div></div>
  </div>
</div>

<div class="container">

  <div class="section">
    <div class="section-title">&#x1F4CA; 핵심 지표</div>
    <div class="grid-3">
      <div class="card"><h3>가장 많은 분야</h3><div class="big">@@TOP_TOPIC_NAME@@</div><div class="sub">@@TOP_TOPIC_SUB@@</div></div>
      <div class="card"><h3>최고 좋아요</h3><div class="big">@@MAX_LIKE@@</div><div class="sub">@@MAX_LIKE_SUB@@</div></div>
      <div class="card"><h3>평균 좋아요</h3><div class="big">@@OVERALL_AVG@@</div><div class="sub">@@BEST_AVG_SUB@@</div></div>
      <div class="card"><h3>최고 관심 키워드</h3><div class="big">@@TOP_KW_BIG@@</div><div class="sub">@@TOP_KW_SUB@@</div></div>
      <div class="card"><h3>일반/기술 vs 로컬</h3><div class="big">@@DIV_RATIO@@</div><div class="sub">@@DIV_SUB@@</div></div>
      <div class="card"><h3>가장 경쟁 적은 분야</h3><div class="big">@@RARE_TOPIC@@</div><div class="sub">@@RARE_SUB@@</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F4C8; 주제별 아이디어 분포</div>
    <p class="section-sub">@@SECTION_TOPIC_LINE@@</p>
    <div class="chart-wrap">
      <div class="chart-title">주제별 아이디어 제출 건수</div>
      <canvas id="topicChart" height="100"></canvas>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x2764;&#xFE0F; 주제별 평균 좋아요 수</div>
    <p class="section-sub">사람들이 실제로 공감한 분야 — 높을수록 시장성 관심도 높음 (빨강 ≥3.5 / 주황 ≥3.0 / 파랑 ≥2.5)</p>
    <div class="chart-wrap">
      <canvas id="likesChart" height="100"></canvas>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F3AF; 공급-수요 매트릭스</div>
    <p class="section-sub">X축: 아이디어 제출 건수(공급), Y축: 평균 좋아요(수요) — 좌상단 = 기회 영역</p>
    <div class="chart-wrap">
      <canvas id="matrixChart" height="75"></canvas>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F524; 빈출 키워드 TOP 30</div>
    <div class="chart-wrap">
      <canvas id="kwChart" height="85"></canvas>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x2601;&#xFE0F; 키워드 클라우드</div>
    <div class="chart-wrap">
      <div class="keyword-cloud" id="kwCloud"></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F967; 분야 구성 비율</div>
    <div class="grid-2">
      <div class="chart-wrap">
        <div class="chart-title">일반/기술 vs 로컬</div>
        <canvas id="divChart"></canvas>
      </div>
      <div class="chart-wrap">
        <div class="chart-title">주제별 비중 (상위 8개)</div>
        <canvas id="topicPieChart"></canvas>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F3C6; 좋아요 TOP 15 아이디어</div>
    <div class="chart-wrap" style="padding:0;overflow:hidden;">
      <table>
        <thead><tr><th>#</th><th>아이디어</th><th>분야</th><th>도전자</th><th>좋아요</th></tr></thead>
        <tbody>""" + top_liked_rows + """</tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F4A1; 핵심 인사이트</div>
    <div class="insight-box insight-blue">
      <h4>&#x1F916; AI 과포화 현상</h4>
      <p>전체 아이디어의 <strong>@@AI_CLASS_PCT@@%(@@AI_CLASS_CNT@@건)</strong>이 AI/머신러닝 주제로 분류. 요약 텍스트에서 'ai' 토큰은 @@AI_KW_N@@회 등장. 단순히 "AI 기반"이라는 수식어만 붙이는 아이디어가 많아 차별성이 희석될 수 있음. <strong>AI 없이 해결하는 접근법</strong>도 차별점이 될 수 있음.</p>
    </div>
    <div class="insight-box insight-green">
      <h4>&#x1F474; 시니어 시장의 높은 공감도</h4>
      <p>시니어/노인 분야는 @@SENIOR_CNT@@건으로 전체의 @@SENIOR_PCT@@%이지만, <strong>평균 좋아요 @@SENIOR_AVG@@</strong>. 고령화 사회에서 시장 규모가 크고 공감도가 높은 편이라 잠재력이 큰 축으로 볼 수 있음.</p>
    </div>
    <div class="insight-box insight-orange">
      <h4>&#x1F3DF;&#xFE0F; 스포츠/레저의 낮은 경쟁</h4>
      <p>스포츠/레저 분야는 <strong>@@SP_CNT@@건</strong>(전체 @@SP_PCT@@%), 평균 좋아요 <strong>@@SP_AVG@@</strong>. 제출 건수 대비 공감도가 높은 편이면 틈새 기회로 볼 수 있음.</p>
    </div>
    <div class="insight-box insight-purple">
      <h4>&#x1F4E6; 물류/배송·HR/채용 — 전문가 영역의 공백</h4>
      <p>물류/배송(@@LOG_CNT@@건)과 HR/채용(@@HR_CNT@@건)은 상대적으로 제안 수가 적은 편. B2B 성격이 강하면 <strong>도메인 전문가에게 기회</strong>가 될 수 있음.</p>
    </div>
    <div class="insight-box insight-red">
      <h4>&#x1F310; 글로벌 진출 아이디어 증가</h4>
      <p>이번 데이터에서 '글로벌' @@KW_GLOBAL@@회, '한국' @@KW_KOREA@@회, '외국인' @@KW_FOREIGN@@회 등장. 해외·다문화 관련 키워드와 함께 글로벌 타깃을 초기에 잡는 접근을 검토할 수 있음.</p>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F31F; 남들이 제안하지 않은 블루오션 분야</div>
    <p class="section-sub">제출 건수 대비 공감도가 높거나, 데이터에서 완전히 빠진 미발굴 영역 8선</p>
    <div class="grid-4opp">

      <div class="opp-card" style="border-color:#3B5BDB;">
        <div class="rank">01</div>
        <h4>&#x1F3DF;&#xFE0F; 스포츠 테크 / 아마추어 스포츠</h4>
        <p style="font-size:0.9rem">동호인 스포츠 리그·매칭·기록 관리, 스포츠 상해 예방, 생활체육 코칭 디지털화. 국내 등록 생활체육 동호인 1,400만 명 대비 IT 도구 극히 부족.</p>
        <div class="why">&#x1F4CA; 제출 @@SP_CNT@@건(@@SP_PCT@@%) · 평균 ♥@@SP_AVG@@</div>
        <div class="meta">
          <span class="badge badge-blue">제출 @@SP_CNT@@건</span>
          <span class="badge badge-red">평균♥ @@SP_AVG@@</span>
          <span class="badge badge-orange">블루오션</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#7048E8;">
        <div class="rank">02</div>
        <h4>&#x1F69A; 물류 혁신 / 라스트마일 특화</h4>
        <p style="font-size:0.9rem">농촌·도서산간 라스트마일 문제, 냉동·의약품 특수 물류, 소규모 역물류(반품) 솔루션. 쿠팡·마켓컬리 이외 틈새 물류 시장은 여전히 공백.</p>
        <div class="why">&#x1F4CA; 제출 @@LOG_CNT@@건 — 상대적으로 소수, 전문가 진입 장벽이 곧 기회</div>
        <div class="meta">
          <span class="badge badge-purple">제출 @@LOG_CNT@@건</span>
          <span class="badge badge-orange">최소 경쟁</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#2F9E44;">
        <div class="rank">03</div>
        <h4>&#x1F477; HR테크 / 현장직·외국인 근로자</h4>
        <p style="font-size:0.9rem">건설·제조·농업 현장 외국인 근로자 HR관리, 비정형 근무자 급여·계약 자동화. '외국인' 키워드 @@KW_FOREIGN@@회, HR/채용 주제 @@HR_CNT@@건.</p>
        <div class="why">&#x1F4CA; HR/채용 평균♥ @@HR_AVG@@ · B2B SaaS 모델 검토</div>
        <div class="meta">
          <span class="badge badge-green">제출 @@HR_CNT@@건</span>
          <span class="badge badge-blue">B2B SaaS</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#F03E3E;">
        <div class="rank">04</div>
        <h4>&#x1F33E; 스마트 농업 / 귀농 플랫폼</h4>
        <p style="font-size:0.9rem">귀농·귀촌 정보 매칭, 농산물 재배 데이터화, 소농 공동판매 플랫폼. 로컬 분야(@@DIV_LOCAL@@건) 대비 농업/농촌 주제는 @@FARM_CNT@@건.</p>
        <div class="why">&#x1F4CA; 고령화 농업 인구 + 청년 귀농 증가 = 구조적 수요 확실</div>
        <div class="meta">
          <span class="badge badge-red">제출 @@FARM_CNT@@건</span>
          <span class="badge badge-green">정책 지원↑</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#E67700;">
        <div class="rank">05</div>
        <h4>&#x267F; 장애인·접근성 보조 기술</h4>
        <p style="font-size:0.9rem">복지/사회문제 @@WELFARE_CNT@@건 중 장애인 특화는 극소수일 수 있음. AI 수어 번역, 시각장애인 내비게이션 등 접근성 보조는 수요가 커지는 축.</p>
        <div class="why">&#x1F4CA; 복지/사회문제 @@WELFARE_CNT@@건 + ESG·공공 수요 맥락</div>
        <div class="meta">
          <span class="badge badge-orange">사회적 가치</span>
          <span class="badge badge-blue">ESG 투자↑</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#0CA678;">
        <div class="rank">06</div>
        <h4>&#x1F30A; 기후변화 / 탄소 크레딧 플랫폼</h4>
        <p style="font-size:0.9rem">환경/에너지 @@ENV_CNT@@건. 탄소·ESG·순환경제 등 세부 테마는 여전히 틈새가 있을 수 있음.</p>
        <div class="why">&#x1F4CA; 2026년 K-ETS 3기 시작 — 제도 변화가 직접적 시장 창출</div>
        <div class="meta">
          <span class="badge badge-green">탄소중립 정책</span>
          <span class="badge badge-blue">B2B 기업 수요</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#AE3EC9;">
        <div class="rank">07</div>
        <h4>&#x1F3D7;&#xFE0F; 건설/건축 디지털화</h4>
        <p style="font-size:0.9rem">BIM 기반 소규모 건축 설계 보조, 하자 진단 AI, 건설 현장 안전관리 SaaS. 대형 시장 대비 건설·건축 키워드에 직접 걸린 제안은 이번 표본에서 많지 않을 수 있음.</p>
        <div class="why">&#x1F4CA; 데이터에서 완전히 빠진 미발굴 영역 — 선점 효과 극대화 가능</div>
        <div class="meta">
          <span class="badge badge-purple">시장 미발굴</span>
          <span class="badge badge-orange">시장 규모↑</span>
        </div>
      </div>

      <div class="opp-card" style="border-color:#1098AD;">
        <div class="rank">08</div>
        <h4>&#x2708;&#xFE0F; 외국인 정착 / 다문화 서비스</h4>
        <p style="font-size:0.9rem">'외국인' 키워드 @@KW_FOREIGN@@회. 국내 정착·행정·언어 지원 등은 여전히 제안 여지가 있는 영역.</p>
        <div class="why">&#x1F4CA; 다문화 가구 40만 + 외국인 유학생 20만 — 빠르게 성장하는 내수 시장</div>
        <div class="meta">
          <span class="badge badge-blue">미발굴 시장</span>
          <span class="badge badge-green">성장세↑</span>
        </div>
      </div>

    </div>
  </div>

  <div class="section">
    <div class="section-title">&#x1F4CB; 분야별 상세 통계</div>
    <div class="chart-wrap" style="padding:0;overflow:hidden;">
      <table>
        <thead><tr><th>분야</th><th>제출 건수</th><th>비중</th><th>평균 좋아요</th><th>총 좋아요</th><th>대표 아이디어</th></tr></thead>
        <tbody>""" + detail_rows + """</tbody>
      </table>
    </div>
  </div>

</div>

<footer>
  <p>&#x1F4CA; 모두의 창업 (modoo.or.kr) 공개 아이디어 데이터 분석 · 수집일: @@FOOTER_DATE@@ · 총 @@TOTAL_CASES_PLAIN@@건</p>
  <p style="margin-top:6px;opacity:0.6">본 보고서는 공개된 아이디어 텍스트를 키워드 기반으로 분류·분석한 결과입니다.</p>
</footer>

<script>
Chart.register(ChartDataLabels);
""" + f"""
const topicLabels = {json.dumps(topic_labels, ensure_ascii=False)};
const topicValues = {json.dumps(topic_values)};
const topicAvgLikes = {json.dumps(topic_avg_likes)};
const kwLabels = {json.dumps(kw_labels[:30], ensure_ascii=False)};
const kwValues = {json.dumps(kw_values[:30])};
const matrixData = {json.dumps(matrix_data_list, ensure_ascii=False)};
const kwCloudData = {json.dumps(kw_items, ensure_ascii=False)};
const divDoughnutData = {json.dumps([div_tech, div_local])};
""" + """
const palette = ['#3B5BDB','#7048E8','#F03E3E','#2F9E44','#E67700','#0CA678','#1098AD','#AE3EC9','#D6336C','#F76707','#74C0FC','#B197FC','#FF8787','#8CE99A','#FFD43B','#63E6BE','#4DABF7','#DA77F2','#F783AC','#FFA94D','#228BE6','#845EF7','#FA5252','#40C057'];

// 1. 주제별 수평 막대
new Chart(document.getElementById('topicChart'), {
  type: 'bar',
  data: { labels: topicLabels, datasets: [{ label: '건수', data: topicValues, backgroundColor: palette, borderRadius: 6 }] },
  options: {
    indexAxis: 'y', responsive: true,
    plugins: { legend: { display: false }, datalabels: { anchor:'end', align:'end', formatter: v => v+'건', font:{size:11,weight:'600'}, color:'#495057' } },
    scales: { x: { grid:{color:'#F1F3F5'}, ticks:{color:'#868E96'} }, y: { grid:{display:false}, ticks:{color:'#212529',font:{size:12}} } }
  }
});

// 2. 평균 좋아요
new Chart(document.getElementById('likesChart'), {
  type: 'bar',
  data: { labels: topicLabels, datasets: [{ label: '평균 좋아요', data: topicAvgLikes, backgroundColor: topicAvgLikes.map(v => v>=3.5?'#F03E3E':v>=3.0?'#E67700':v>=2.5?'#3B5BDB':'#ADB5BD'), borderRadius: 6 }] },
  options: {
    indexAxis: 'y', responsive: true,
    plugins: { legend: { display: false }, datalabels: { anchor:'end', align:'end', formatter: v => '♥ '+v, font:{size:11,weight:'600'}, color:'#495057' } },
    scales: { x: { grid:{color:'#F1F3F5'}, ticks:{color:'#868E96'} }, y: { grid:{display:false}, ticks:{color:'#212529',font:{size:12}} } }
  }
});

// 3. 매트릭스 산점도
new Chart(document.getElementById('matrixChart'), {
  type: 'scatter',
  data: { datasets: [{ label: '분야', data: matrixData, backgroundColor: matrixData.map((d,i) => palette[i%palette.length]+'CC'), pointRadius: matrixData.map(d => Math.sqrt(d.x)*0.8+5), pointHoverRadius: 10 }] },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => `${ctx.raw.label}: 제출 ${ctx.raw.x}건, 평균♥ ${ctx.raw.y}` } },
      datalabels: { formatter: v => v.label, font:{size:10,weight:'600'}, color:'#212529', offset:8, align:'top' }
    },
    scales: {
      x: { title:{display:true, text:'제출 건수 (공급) →', color:'#495057', font:{size:12}}, grid:{color:'#F1F3F5'} },
      y: { title:{display:true, text:'평균 좋아요 (수요) ↑', color:'#495057', font:{size:12}}, grid:{color:'#F1F3F5'} }
    }
  }
});

// 4. 키워드 막대
new Chart(document.getElementById('kwChart'), {
  type: 'bar',
  data: { labels: kwLabels, datasets: [{ label: '언급 횟수', data: kwValues, backgroundColor: kwValues.map((v,i) => i===0?'#F03E3E':i<5?'#E67700':i<15?'#3B5BDB':'#ADB5BD'), borderRadius: 4 }] },
  options: {
    responsive: true,
    plugins: { legend:{display:false}, datalabels:{display:false} },
    scales: { x:{grid:{display:false}, ticks:{color:'#495057',font:{size:11}}}, y:{grid:{color:'#F1F3F5'}, ticks:{color:'#868E96'}} }
  }
});

// 5. 분야 도넛
new Chart(document.getElementById('divChart'), {
  type: 'doughnut',
  data: { labels: ['일반/기술','로컬'], datasets: [{ data: divDoughnutData, backgroundColor:['#3B5BDB','#2F9E44'], borderWidth:3, borderColor:'#fff' }] },
  options: { responsive:true, plugins: { legend:{position:'bottom'}, datalabels:{ formatter:(v,ctx)=>{const t=ctx.dataset.data.reduce((a,b)=>a+b,0); return (v/t*100).toFixed(1)+'%';}, color:'#fff', font:{size:14,weight:'700'} } } }
});

// 6. 주제 파이
new Chart(document.getElementById('topicPieChart'), {
  type: 'pie',
  data: { labels: topicLabels.slice(0,8), datasets: [{ data: topicValues.slice(0,8), backgroundColor: palette.slice(0,8), borderWidth:3, borderColor:'#fff' }] },
  options: { responsive:true, plugins: { legend:{position:'bottom',labels:{font:{size:11}}}, datalabels:{ formatter:(v,ctx)=>{const t=ctx.dataset.data.reduce((a,b)=>a+b,0); return (v/t*100).toFixed(1)+'%';}, color:'#fff', font:{size:11,weight:'700'} } } }
});

// 키워드 클라우드
const maxCount = kwCloudData[0][1];
const cloudEl = document.getElementById('kwCloud');
kwCloudData.forEach(([word, count]) => {
  const span = document.createElement('span');
  const ratio = count / maxCount;
  span.className = 'kw-item ' + (ratio > 0.7 ? 'kw-large' : ratio > 0.35 ? 'kw-medium' : 'kw-small');
  span.textContent = word + ' ' + count;
  cloudEl.appendChild(span);
});
</script>
</body>
</html>"""

_repl = {
    "@@TOTAL_CASES@@": f"{total:,}건",
    "@@TOTAL_CASES_PLAIN@@": f"{total:,}",
    "@@N_TOPICS@@": str(n_topics),
    "@@AI_KW_HITS@@": f"{ai_kw_hits:,}회",
    "@@AI_KW_N@@": f"{ai_kw_hits:,}",
    "@@HERO_DATE@@": hero_date,
    "@@FOOTER_DATE@@": hero_date,
    "@@TOP_TOPIC_NAME@@": top_topic_name,
    "@@TOP_TOPIC_SUB@@": f"{top_topic_count:,}건 · 전체의 {top_topic_pct}%",
    "@@MAX_LIKE@@": f"{max_like:,}개",
    "@@MAX_LIKE_SUB@@": max_like_blurb,
    "@@OVERALL_AVG@@": f"{overall_avg}개",
    "@@BEST_AVG_SUB@@": (
        f"{best_topic_name} 분야 평균 ♥{best_topic_avg} (제출 5건 이상 중)"
        if best_topic_name != "-"
        else "표본 부족"
    ),
    "@@TOP_KW_BIG@@": top_kw_big,
    "@@TOP_KW_SUB@@": f"{top_kw_count:,}회 언급 · 전체 {top_kw_pct}%",
    "@@DIV_RATIO@@": f"{pct_tech}% : {pct_loc}%",
    "@@DIV_SUB@@": f"일반/기술 {div_tech:,}건 / 로컬 {div_local:,}건",
    "@@RARE_TOPIC@@": rare_topic_name,
    "@@RARE_SUB@@": (
        f"{rare_topic_cnt:,}건 · 평균 좋아요 {rare_topic_avg}"
        if rare_topic_name != "-"
        else "-"
    ),
    "@@SECTION_TOPIC_LINE@@": f"전체 {total:,}건을 {n_topics}개 주제 라벨로 분류 (중복 포함, 키워드 기준)",
    "@@AI_CLASS_PCT@@": f"{ai_class_pct:.1f}",
    "@@AI_CLASS_CNT@@": f"{ai_class_cnt:,}",
    "@@SENIOR_CNT@@": f"{senior_cnt:,}",
    "@@SENIOR_PCT@@": f"{senior_pct:.1f}",
    "@@SENIOR_AVG@@": f"{senior_avg:.2f}",
    "@@SP_CNT@@": f"{sp_cnt:,}",
    "@@SP_PCT@@": f"{sp_pct:.1f}",
    "@@SP_AVG@@": f"{sp_avg:.2f}",
    "@@LOG_CNT@@": f"{log_cnt:,}",
    "@@HR_CNT@@": f"{hr_cnt:,}",
    "@@HR_AVG@@": f"{hr_avg:.2f}",
    "@@KW_GLOBAL@@": f"{kw_global:,}",
    "@@KW_KOREA@@": f"{kw_korea:,}",
    "@@KW_FOREIGN@@": f"{kw_foreign:,}",
    "@@DIV_LOCAL@@": f"{div_local:,}",
    "@@FARM_CNT@@": f"{farm_cnt:,}",
    "@@WELFARE_CNT@@": f"{welfare_cnt:,}",
    "@@ENV_CNT@@": f"{env_cnt:,}",
}
for _k, _v in _repl.items():
    html = html.replace(_k, _v)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print(f"완료: {REPORT_PATH}")
print(f"파일 크기: {len(html):,} bytes")
