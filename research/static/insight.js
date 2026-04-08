/* Insight 보고서 — Chart.js, GET /api/insight */
(function () {
  "use strict";

  const COLORS = {
    primary: "#3B5BDB",
    blue: "#4C6EF5",
    green: "#2F9E44",
    orange: "#F76707",
    purple: "#7048E8",
    teal: "#0CA678",
    gray: "#868E96",
    red: "#E03131",
  };

  const PALETTE = [
    "#4C6EF5", "#F76707", "#2F9E44", "#AE3EC9", "#0CA678",
    "#E03131", "#F59F00", "#1098AD", "#D6336C", "#74B816",
    "#3B5BDB", "#C2255C", "#37B24D", "#845EF7", "#FD7E14",
  ];

  const charts = {};

  function destroy(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  }

  function mkChart(id, config) {
    destroy(id);
    const el = document.getElementById(id);
    if (!el) return null;
    charts[id] = new Chart(el, config);
    return charts[id];
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  function pct(part, total) {
    if (!total) return "0";
    return ((part / total) * 100).toFixed(1);
  }

  function renderQuant(d, total) {
    const q = d.quantitative;
    const cl = q.clusters || {};

    document.getElementById("kpiClusters").textContent = (cl.cluster_count ?? "-").toLocaleString();
    document.getElementById("kpiMultiClusters").textContent = (cl.multi_idea_clusters ?? "-").toLocaleString();
    document.getElementById("kpiLargestCluster").textContent = (cl.largest_cluster_size ?? "-").toLocaleString();
    const aiPct = pct(q.ai_usage.yes, total);
    document.getElementById("kpiAiPct").textContent = `${aiPct}%`;

    const divE = Object.entries(q.by_division || {}).sort((a, b) => b[1] - a[1]);
    mkChart("chartByDivision", {
      type: "bar",
      data: {
        labels: divE.map(e => e[0]),
        datasets: [{ label: "건수", data: divE.map(e => e[1]), backgroundColor: PALETTE.slice(0, divE.length) }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const probE = Object.entries(q.problem_type || {});
    mkChart("chartProblemType", {
      type: "doughnut",
      data: {
        labels: probE.map(e => e[0]),
        datasets: [{ data: probE.map(e => e[1]), backgroundColor: PALETTE }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right" },
          tooltip: {
            callbacks: {
              label: ctx => {
                const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                return `${ctx.label}: ${ctx.parsed}건 (${pct(ctx.parsed, sum)}%)`;
              },
            },
          },
        },
      },
    });

    const custE = Object.entries(q.customer_segment || {});
    mkChart("chartCustomer", {
      type: "pie",
      data: {
        labels: custE.map(e => e[0]),
        datasets: [{ data: custE.map(e => e[1]), backgroundColor: PALETTE }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "right", labels: { boxWidth: 10, font: { size: 10 } } } },
      },
    });

    mkChart("chartAI", {
      type: "doughnut",
      data: {
        labels: ["AI·생성형 등 언급", "미언급"],
        datasets: [{
          data: [q.ai_usage.yes, q.ai_usage.no],
          backgroundColor: [COLORS.purple, COLORS.gray],
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });

    const b2 = Object.entries(q.b2x || {});
    mkChart("chartB2x", {
      type: "pie",
      data: {
        labels: b2.map(e => e[0]),
        datasets: [{ data: b2.map(e => e[1]), backgroundColor: [COLORS.blue, COLORS.teal, COLORS.orange] }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });

    const kw = (q.top_keywords || []).slice(0, 20);
    mkChart("chartKeywords", {
      type: "bar",
      data: {
        labels: kw.map(k => k.word),
        datasets: [{ label: "빈도", data: kw.map(k => k.count), backgroundColor: COLORS.primary }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const tbody = document.querySelector("#clusterSampleTable tbody");
    const samples = cl.sample_clusters || [];
    tbody.innerHTML = samples.length
      ? samples.map(s =>
        `<tr><td>${s.size}건</td><td>${(s.top_keywords || []).map(escapeHtml).join(", ")}</td></tr>`
      ).join("")
      : `<tr><td colspan="2">표본 없음</td></tr>`;

    const topProb = [...probE].sort((a, b) => b[1] - a[1])[0];
    const topCust = [...custE].sort((a, b) => b[1] - a[1])[0];
    document.getElementById("insightQuant").innerHTML =
      `<strong>정량 인사이트</strong>
      <ul>
        <li>대분야는 <strong>${divE[0]?.[0] || "-"}</strong>가 ${divE[0]?.[1]?.toLocaleString() || 0}건으로 가장 많습니다.</li>
        <li>문제·가치 유형은 <strong>${topProb?.[0] || "-"}</strong> 비중이 ${pct(topProb?.[1] || 0, total)}%입니다.</li>
        <li>고객군 추정 상위는 <strong>${topCust?.[0] || "-"}</strong>이며, 전체의 약 ${pct(topCust?.[1] || 0, total)}%입니다.</li>
        <li>AI 관련 언급은 <strong>${q.ai_usage.yes.toLocaleString()}건 (${aiPct}%)</strong>입니다.</li>
        <li>토큰 공유 기준 유사 연결군은 <strong>${cl.multi_idea_clusters ?? 0}개</strong>(2건 이상 묶임), 전체 연결요소 <strong>${cl.cluster_count ?? 0}개</strong>입니다.</li>
      </ul>`;
  }

  function renderQual(d, total) {
    const ql = d.qualitative;
    const motE = Object.entries(ql.motivation || {});

    mkChart("chartMotivation", {
      type: "doughnut",
      data: {
        labels: motE.map(e => e[0]),
        datasets: [{ data: motE.map(e => e[1]), backgroundColor: PALETTE }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "right", labels: { boxWidth: 10, font: { size: 10 } } } },
      },
    });

    const hx = ql.hype_vs_execution || {};
    mkChart("chartHypeExec", {
      type: "bar",
      data: {
        labels: ["과장 키워드만", "실행 키워드만", "둘 다", "둘 다 없음"],
        datasets: [{
          label: "건수",
          data: [hx.hype_only, hx.execution_only, hx.both, hx.neither],
          backgroundColor: [COLORS.orange, COLORS.green, COLORS.purple, COLORS.gray],
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const sk = (ql.social_impact_keywords || []).slice(0, 15);
    mkChart("chartSocialKw", {
      type: "bar",
      data: {
        labels: sk.map(k => k.word),
        datasets: [{ label: "빈도", data: sk.map(k => k.count), backgroundColor: COLORS.teal }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const lk = (ql.local_top_keywords || []).slice(0, 15);
    mkChart("chartLocalKw", {
      type: "bar",
      data: {
        labels: lk.map(k => k.word),
        datasets: [{ label: "빈도", data: lk.map(k => k.count), backgroundColor: COLORS.green }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const twBody = document.querySelector("#techWeakTable tbody");
    const tw = ql.tech_weak_samples || [];
    twBody.innerHTML = tw.length
      ? tw.map(row =>
        `<tr><td>${escapeHtml(row.subcategory)}</td><td>${escapeHtml(row.summary)}</td><td class="likes-col">${row.likes}</td></tr>`
      ).join("")
      : `<tr><td colspan="3">해당 패턴 샘플이 없습니다.</td></tr>`;

    const execRatio = pct((hx.execution_only || 0) + (hx.both || 0), total);
    document.getElementById("insightQual").innerHTML =
      `<strong>정성 인사이트</strong>
      <ul>
        <li>창업 동기 추정 상위 유형은 키워드 매칭 기준으로 도출되었습니다.</li>
        <li>실행·검증 키워드(시장조사, MVP 등)가 포함된 비율은 약 <strong>${execRatio}%</strong>입니다.</li>
        <li>사회·임팩트 관련 키워드가 있는 아이디어는 <strong>${(ql.social_idea_count || 0).toLocaleString()}건</strong>입니다.</li>
        <li>로컬 분야(${ (ql.local_idea_count || 0).toLocaleString()}건)의 상위 키워드는 지역·생활 밀착 소비·서비스 성격을 반영합니다.</li>
        <li>기술 키워드는 있으나 고객·시장 언급이 적은 요약은 <strong>Go-to-market 서술 보강</strong>이 필요한 후보로 볼 수 있습니다.</li>
      </ul>`;
  }

  function renderStrat(d, total) {
    const st = d.strategic;
    const crowded = st.crowded_subcategories || [];
    mkChart("chartCrowded", {
      type: "bar",
      data: {
        labels: crowded.map(x => x.subcategory),
        datasets: [{ label: "등록 건수", data: crowded.map(x => x.count), backgroundColor: COLORS.red }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const sparse = st.sparse_subcategories || [];
    mkChart("chartSparse", {
      type: "bar",
      data: {
        labels: sparse.map(x => x.subcategory),
        datasets: [{ label: "등록 건수", data: sparse.map(x => x.count), backgroundColor: COLORS.teal }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const divSc = Object.entries(st.avg_commercialization_by_division || {});
    const divScoreVals = divSc.map(e => e[1]);
    const rMax = divScoreVals.length ? Math.max(5, Math.max(...divScoreVals) + 0.5) : 5;
    mkChart("chartRadarDiv", {
      type: "radar",
      data: {
        labels: divSc.map(e => e[0]),
        datasets: [{
          label: "평균 사업화 점수",
          data: divSc.map(e => e[1]),
          borderColor: COLORS.primary,
          backgroundColor: "rgba(59, 91, 219, 0.2)",
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            suggestedMax: rMax,
          },
        },
        plugins: { legend: { display: false } },
      },
    });

    const topSub = (st.top_subcategories_by_commercialization_score || []).slice(0, 10);
    mkChart("chartSubScore", {
      type: "bar",
      data: {
        labels: topSub.map(x => x.subcategory),
        datasets: [{ label: "평균 점수", data: topSub.map(x => x.avg_score), backgroundColor: COLORS.orange }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const sup = st.support_needed || [];
    document.querySelector("#supportTable tbody").innerHTML = sup.length
      ? sup.map(r =>
        `<tr><td>${escapeHtml(r.subcategory)}</td><td>${r.count}</td><td>${r.avg_likes}</td><td>${r.total_likes}</td></tr>`
      ).join("")
      : `<tr><td colspan="4">조건에 맞는 항목이 없습니다.</td></tr>`;

    const samples = d.scores?.per_idea_sample || [];
    document.querySelector("#scoreSampleTable tbody").innerHTML = samples.map(r =>
      `<tr><td>${r.index ?? ""}</td><td>${escapeHtml(r.summary)}</td><td><strong>${r.score}</strong></td></tr>`
    ).join("");

    const topCrowded = crowded[0];
    const topScoreSub = topSub[0];
    const supList = sup.slice(0, 3).map(r => `<strong>${escapeHtml(r.subcategory)}</strong>(평균 좋아요 ${r.avg_likes})`).join(", ");
    document.getElementById("insightStrat").innerHTML =
      `<strong>전략 인사이트</strong>
      <ul>
        <li><strong>과밀 영역:</strong> ${topCrowded ? `${escapeHtml(topCrowded.subcategory)}(${topCrowded.count}건)` : "-"} 등 — 차별화·닛치 전략이 필요합니다.</li>
        <li><strong>미충족·저밀도 후보:</strong> 건수는 적으나 블루오션 탐색 시 참고할 수 있습니다(하위 5개 차트).</li>
        <li><strong>후속 지원·홍보:</strong> ${supList || "해당 없음"} — 노출 대비 반응이 낮을 수 있어 멘토링·데모데이 연계를 검토할 만합니다.</li>
        <li><strong>사업화 잠재(휴리스틱):</strong> 세부분야 평균 점수 상위는 <strong>${topScoreSub ? escapeHtml(topScoreSub.subcategory) : "-"}</strong> 등입니다. 점수는 요약 길이·실행/시장 키워드·좋아요를 가중한 추정치입니다.</li>
      </ul>`;
  }

  async function init() {
    try {
      const res = await fetch("/api/insight");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      if (d.empty) {
        document.getElementById("meta").textContent = "데이터가 없습니다. 먼저 수집을 실행하세요.";
        document.getElementById("loadingOverlay").classList.add("hidden");
        return;
      }
      const total = d.meta.total;
      document.getElementById("meta").textContent =
        `전체 ${total.toLocaleString()}건 · 수집일: ${d.meta.crawled_at ? String(d.meta.crawled_at).slice(0, 10) : "-"}`;

      renderQuant(d, total);
      renderQual(d, total);
      renderStrat(d, total);

      document.getElementById("loadingOverlay").classList.add("hidden");
    } catch (e) {
      console.error(e);
      document.getElementById("meta").textContent = "Insight API 로드 실패 (/api/insight)";
      document.getElementById("loadingOverlay").classList.add("hidden");
    }
  }

  init();
})();
