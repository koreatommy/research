/* ==========================================================================
   analytics.js — 데이터분석 보고서 차트 렌더링
   Chart.js v4 + chartjs-chart-matrix
   ========================================================================== */

(function () {
  "use strict";

  const COLORS = {
    primary: "#3B5BDB",
    primaryLight: "#DBE4FF",
    blue: "#4C6EF5",
    green: "#2F9E44",
    greenLight: "#D3F9D8",
    red: "#E03131",
    orange: "#F76707",
    purple: "#7048E8",
    teal: "#0CA678",
    gray: "#868E96",
    border: "#DEE2E6",
  };

  const PALETTE = [
    "#4C6EF5", "#F76707", "#2F9E44", "#AE3EC9", "#0CA678",
    "#E03131", "#F59F00", "#1098AD", "#D6336C", "#74B816",
    "#3B5BDB", "#C2255C", "#37B24D", "#845EF7", "#FD7E14",
    "#12B886", "#FA5252", "#7950F2", "#40C057", "#E64980",
    "#15AABF", "#FF6B6B",
  ];

  const chartInstances = {};

  function destroyChart(id) {
    if (chartInstances[id]) {
      chartInstances[id].destroy();
      delete chartInstances[id];
    }
  }

  function createChart(id, config) {
    destroyChart(id);
    const ctx = document.getElementById(id);
    if (!ctx) return null;
    chartInstances[id] = new Chart(ctx, config);
    return chartInstances[id];
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  // -----------------------------------------------------------------------
  // Section 1: KPI + 대분야 도넛
  // -----------------------------------------------------------------------
  function renderSummary(data) {
    const m = data.meta;
    document.getElementById("kpiTotal").textContent = m.total.toLocaleString();
    document.getElementById("kpiContributors").textContent = m.total_contributors.toLocaleString();
    document.getElementById("kpiAvgLikes").textContent = data.likes_analysis.avg_likes;
    document.getElementById("kpiTotalLikes").textContent = data.likes_analysis.total_likes.toLocaleString();
    document.getElementById("kpiSubcategories").textContent = m.subcategory_count;
    document.getElementById("kpiDate").textContent = m.crawled_at ? m.crawled_at.slice(0, 10) : "-";
    document.getElementById("meta").textContent =
      `전체 ${m.total.toLocaleString()}건 · 수집일: ${m.crawled_at ? m.crawled_at.slice(0, 10) : "-"}`;

    const divDist = data.division_distribution;
    const divLabels = Object.keys(divDist);
    const divValues = Object.values(divDist);

    createChart("chartDivisionDonut", {
      type: "doughnut",
      data: {
        labels: divLabels,
        datasets: [{ data: divValues, backgroundColor: [COLORS.blue, COLORS.green, COLORS.purple, COLORS.orange].slice(0, divLabels.length) }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
          tooltip: {
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                return `${ctx.label}: ${ctx.parsed.toLocaleString()}건 (${pct}%)`;
              },
            },
          },
        },
      },
    });

    const contribByDiv = data.contributor_analysis.contributor_by_division;
    createChart("chartDivisionContributors", {
      type: "doughnut",
      data: {
        labels: Object.keys(contribByDiv),
        datasets: [{ data: Object.values(contribByDiv), backgroundColor: [COLORS.blue, COLORS.green, COLORS.purple, COLORS.orange] }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });
  }

  // -----------------------------------------------------------------------
  // Section 2: 분야 분포
  // -----------------------------------------------------------------------
  function renderDistribution(data) {
    const subDist = data.subcategory_distribution;
    const sorted = Object.entries(subDist).sort((a, b) => b[1] - a[1]);
    const labels = sorted.map(e => e[0]);
    const values = sorted.map(e => e[1]);

    createChart("chartSubcategoryBar", {
      type: "bar",
      data: {
        labels,
        datasets: [{ label: "아이디어 수", data: values, backgroundColor: PALETTE.slice(0, labels.length) }],
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const subByDiv = data.subcategory_by_division;
    renderStackChart("chartTechStack", subByDiv["일반/기술"] || {});
    renderStackChart("chartLocalStack", subByDiv["로컬"] || {});

    const top3 = sorted.slice(0, 3).map(e => `${e[0]}(${e[1]}건)`).join(", ");
    const totalIdeas = data.meta.total;
    const techCount = (data.division_distribution["일반/기술"] || 0);
    const localCount = (data.division_distribution["로컬"] || 0);
    const techPct = ((techCount / totalIdeas) * 100).toFixed(1);
    const localPct = ((localCount / totalIdeas) * 100).toFixed(1);

    document.getElementById("insightDistribution").innerHTML =
      `<strong>분포 분석 인사이트</strong>
      <ul>
        <li>상위 3개 세부분야: ${top3} — 전체의 상당 비중을 차지합니다.</li>
        <li>일반/기술(${techPct}%) vs 로컬(${localPct}%): 기술·산업 중심 아이디어가 주류입니다.</li>
        <li>세부분야 22개 중 상위 5개가 전체의 ${((sorted.slice(0, 5).reduce((s, e) => s + e[1], 0) / totalIdeas) * 100).toFixed(1)}%를 차지해 집중도가 높습니다.</li>
      </ul>`;
  }

  function renderStackChart(canvasId, subData) {
    const sorted = Object.entries(subData).sort((a, b) => b[1] - a[1]);
    createChart(canvasId, {
      type: "doughnut",
      data: {
        labels: sorted.map(e => e[0]),
        datasets: [{ data: sorted.map(e => e[1]), backgroundColor: PALETTE.slice(0, sorted.length) }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } },
          tooltip: {
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                return `${ctx.label}: ${ctx.parsed.toLocaleString()}건 (${((ctx.parsed / total) * 100).toFixed(1)}%)`;
              },
            },
          },
        },
      },
    });
  }

  // -----------------------------------------------------------------------
  // Section 3: 시계열
  // -----------------------------------------------------------------------
  let timeSeriesData = {};

  function renderTimeSeries(data) {
    timeSeriesData = data.time_series;
    drawTimeSeriesChart("monthly");

    document.querySelectorAll(".toggle-btn[data-period]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".toggle-btn[data-period]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        drawTimeSeriesChart(btn.dataset.period);
      });
    });

    const divMonthly = data.time_series.division_monthly;
    const allMonths = Object.values(divMonthly)[0]?.map(e => e.month) || [];
    const datasets = Object.entries(divMonthly).map(([div, arr], i) => ({
      label: div,
      data: arr.map(e => e.count),
      borderColor: PALETTE[i],
      backgroundColor: PALETTE[i] + "33",
      tension: 0.3,
      fill: false,
    }));

    createChart("chartDivisionMonthly", {
      type: "line",
      data: { labels: allMonths, datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: "top" } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const weekday = data.time_series.weekday;
    createChart("chartWeekday", {
      type: "bar",
      data: {
        labels: weekday.map(e => e.day),
        datasets: [{ label: "등록 수", data: weekday.map(e => e.count), backgroundColor: COLORS.blue }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const hourly = data.time_series.hourly;
    createChart("chartHourly", {
      type: "bar",
      data: {
        labels: hourly.map(e => `${e.hour}시`),
        datasets: [{ label: "등록 수", data: hourly.map(e => e.count), backgroundColor: COLORS.teal }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const peakWeekday = weekday.reduce((a, b) => a.count > b.count ? a : b);
    const peakHour = hourly.reduce((a, b) => a.count > b.count ? a : b);
    const monthlyArr = data.time_series.monthly;
    const peakMonth = monthlyArr.length ? monthlyArr.reduce((a, b) => a.count > b.count ? a : b) : null;

    document.getElementById("insightTemporal").innerHTML =
      `<strong>시계열 분석 인사이트</strong>
      <ul>
        <li>가장 활발한 요일: <strong>${peakWeekday.day}요일</strong> (${peakWeekday.count.toLocaleString()}건)</li>
        <li>가장 활발한 시간대: <strong>${peakHour.hour}시</strong> (${peakHour.count.toLocaleString()}건)</li>
        ${peakMonth ? `<li>피크 월: <strong>${peakMonth.month}</strong> (${peakMonth.count.toLocaleString()}건) — 시기별 관심 변화를 보여줍니다.</li>` : ""}
      </ul>`;
  }

  function drawTimeSeriesChart(period) {
    let items, labelKey;
    if (period === "daily") { items = timeSeriesData.daily; labelKey = "date"; }
    else if (period === "weekly") { items = timeSeriesData.weekly; labelKey = "week"; }
    else { items = timeSeriesData.monthly; labelKey = "month"; }

    createChart("chartTimeSeries", {
      type: "line",
      data: {
        labels: items.map(e => e[labelKey]),
        datasets: [{
          label: "아이디어 수",
          data: items.map(e => e.count),
          borderColor: COLORS.primary,
          backgroundColor: COLORS.primaryLight,
          tension: 0.3,
          fill: true,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true },
          x: { ticks: { maxTicksLimit: 20 } },
        },
      },
    });
  }

  // -----------------------------------------------------------------------
  // Section 4: 참여도
  // -----------------------------------------------------------------------
  function renderEngagement(data) {
    const la = data.likes_analysis;

    createChart("chartLikesDist", {
      type: "bar",
      data: {
        labels: la.likes_distribution.map(e => e.range),
        datasets: [{ label: "아이디어 수", data: la.likes_distribution.map(e => e.count), backgroundColor: COLORS.red }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const subLikes = la.likes_by_subcategory;
    const sorted = Object.entries(subLikes).sort((a, b) => b[1].avg - a[1].avg);

    createChart("chartSubLikes", {
      type: "bar",
      data: {
        labels: sorted.map(e => e[0]),
        datasets: [{ label: "평균 좋아요", data: sorted.map(e => e[1].avg), backgroundColor: COLORS.orange }],
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const tbody = document.querySelector("#topLikedTable tbody");
    tbody.innerHTML = la.top_liked_ideas.map((item, i) =>
      `<tr>
        <td>${i + 1}</td>
        <td>${escapeHtml(item.summary)}</td>
        <td><span class="badge ${item.division === "일반/기술" ? "badge-blue" : "badge-green"}">${escapeHtml(item.division)}</span></td>
        <td>${escapeHtml(item.subcategory)}</td>
        <td>${escapeHtml(item.nickname)}</td>
        <td class="likes-col">&#x2665; ${item.likes}</td>
        <td>${item.created_at}</td>
      </tr>`
    ).join("");

    const zeroCount = la.likes_distribution.find(e => e.range === "0")?.count || 0;
    const zeroPct = ((zeroCount / data.meta.total) * 100).toFixed(1);
    const topSub = sorted[0];

    document.getElementById("insightEngagement").innerHTML =
      `<strong>참여도 분석 인사이트</strong>
      <ul>
        <li>좋아요 0인 아이디어: <strong>${zeroCount.toLocaleString()}건 (${zeroPct}%)</strong> — 대다수가 미참여 상태로, 롱테일 분포를 보입니다.</li>
        <li>세부분야 평균 좋아요 최고: <strong>${topSub[0]}</strong> (${topSub[1].avg}) — 양적 규모와 인기도가 반드시 비례하지 않습니다.</li>
        <li>최다 좋아요: <strong>${la.max_likes}개</strong>, 중앙값: <strong>${la.median_likes}</strong> — 극소수 아이디어에 좋아요가 집중됩니다.</li>
      </ul>`;
  }

  // -----------------------------------------------------------------------
  // Section 5: 참여자
  // -----------------------------------------------------------------------
  function renderContributors(data) {
    const ca = data.contributor_analysis;

    createChart("chartContribType", {
      type: "doughnut",
      data: {
        labels: ["1회 참여", "반복 참여"],
        datasets: [{
          data: [ca.single_idea_contributors, ca.repeat_contributors],
          backgroundColor: [COLORS.gray, COLORS.blue],
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
          tooltip: {
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                return `${ctx.label}: ${ctx.parsed.toLocaleString()}명 (${((ctx.parsed / total) * 100).toFixed(1)}%)`;
              },
            },
          },
        },
      },
    });

    const dist = ca.contributor_idea_distribution;
    const distOrder = ["1건", "2-3건", "4-5건", "6-10건", "11건+"];
    const distLabels = distOrder.filter(k => dist[k] !== undefined);
    const distValues = distLabels.map(k => dist[k]);

    createChart("chartContribDist", {
      type: "bar",
      data: {
        labels: distLabels,
        datasets: [{ label: "참여자 수", data: distValues, backgroundColor: COLORS.purple }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const topC = ca.top_contributors;
    createChart("chartTopContrib", {
      type: "bar",
      data: {
        labels: topC.map(e => e.nickname),
        datasets: [{ label: "아이디어 수", data: topC.map(e => e.count), backgroundColor: COLORS.teal }],
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    document.getElementById("insightContributors").innerHTML =
      `<strong>참여자 분석 인사이트</strong>
      <ul>
        <li>총 참여자: <strong>${ca.total_contributors.toLocaleString()}명</strong>, 1인당 평균 <strong>${ca.ideas_per_contributor_avg}건</strong></li>
        <li>1회성 참여자: <strong>${ca.single_idea_contributors_pct}%</strong> — 대다수가 단발성 참여입니다.</li>
        <li>상위 참여자(${topC[0]?.nickname || "-"}: ${topC[0]?.count || 0}건)가 커뮤니티 활동을 주도합니다.</li>
      </ul>`;
  }

  // -----------------------------------------------------------------------
  // Section 6: 교차 분석
  // -----------------------------------------------------------------------
  function renderCrossAnalysis(data) {
    const cross = data.cross_analysis;

    renderHeatmap(cross.heatmap_data, cross.all_months);

    const divLR = cross.division_like_range;
    const rangeLabels = ["0", "1", "2-5", "6-10", "11-50", "51+"];
    const divNames = Object.keys(divLR);
    const datasets = divNames.map((d, i) => ({
      label: d,
      data: rangeLabels.map(r => divLR[d]?.[r] || 0),
      backgroundColor: PALETTE[i],
    }));

    createChart("chartDivLikeRange", {
      type: "bar",
      data: { labels: rangeLabels.map(r => `좋아요 ${r}`), datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: "top" } },
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
      },
    });

    const diversity = cross.subcategory_contributor_diversity;
    const sorted = Object.entries(diversity).sort((a, b) => b[1].hhi - a[1].hhi);

    createChart("chartDiversityHHI", {
      type: "bar",
      data: {
        labels: sorted.map(e => e[0]),
        datasets: [{
          label: "HHI (높을수록 집중)",
          data: sorted.map(e => e[1].hhi),
          backgroundColor: sorted.map(e => e[1].hhi > 0.1 ? COLORS.red : COLORS.green),
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, max: 1 } },
      },
    });

    const hourDiv = cross.hour_by_division;
    const hourLabels = Array.from({ length: 24 }, (_, i) => `${i}시`);
    const hourDatasets = Object.entries(hourDiv).map(([d, arr], i) => ({
      label: d,
      data: arr.map(e => e.count),
      borderColor: PALETTE[i],
      backgroundColor: PALETTE[i] + "33",
      tension: 0.3,
      fill: false,
    }));

    createChart("chartHourDiv", {
      type: "line",
      data: { labels: hourLabels, datasets: hourDatasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: "top" } },
        scales: { y: { beginAtZero: true } },
      },
    });

    const highHHI = sorted.filter(e => e[1].hhi > 0.1).slice(0, 3);
    const lowHHI = sorted.filter(e => e[1].hhi <= 0.05).slice(-3).reverse();
    document.getElementById("insightCross").innerHTML =
      `<strong>교차 분석 인사이트</strong>
      <ul>
        <li>참여자 집중도(HHI) 높은 분야: ${highHHI.map(e => `<strong>${e[0]}</strong>(${e[1].hhi})`).join(", ") || "없음"} — 소수 참여자가 주도합니다.</li>
        <li>참여자 다양성 높은 분야: ${lowHHI.map(e => `<strong>${e[0]}</strong>(${e[1].hhi})`).join(", ") || "없음"} — 많은 사람이 고루 참여합니다.</li>
        <li>히트맵을 통해 시기별 관심 분야의 이동 패턴을 확인할 수 있습니다.</li>
      </ul>`;
  }

  function renderHeatmap(heatmapData, allMonths) {
    if (!heatmapData || !heatmapData.length || typeof Chart.registry.controllers.get("matrix") === "undefined") {
      renderHeatmapFallback(heatmapData, allMonths);
      return;
    }

    const subcategories = [...new Set(heatmapData.map(e => e.subcategory))];
    const maxVal = Math.max(...heatmapData.map(e => e.count), 1);

    const matrixData = heatmapData.map(e => ({
      x: allMonths.indexOf(e.month),
      y: subcategories.indexOf(e.subcategory),
      v: e.count,
    }));

    createChart("chartHeatmap", {
      type: "matrix",
      data: {
        datasets: [{
          label: "아이디어 수",
          data: matrixData,
          backgroundColor(ctx) {
            const v = ctx.dataset.data[ctx.dataIndex]?.v || 0;
            const alpha = Math.max(0.08, v / maxVal);
            return `rgba(59, 91, 219, ${alpha})`;
          },
          width: ({ chart }) => (chart.chartArea?.width || 600) / allMonths.length - 2,
          height: ({ chart }) => (chart.chartArea?.height || 400) / subcategories.length - 2,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: () => "",
              label(ctx) {
                const d = ctx.dataset.data[ctx.dataIndex];
                return `${subcategories[d.y]} / ${allMonths[d.x]}: ${d.v}건`;
              },
            },
          },
        },
        scales: {
          x: {
            type: "category",
            labels: allMonths,
            offset: true,
            ticks: { font: { size: 10 } },
            grid: { display: false },
          },
          y: {
            type: "category",
            labels: subcategories,
            offset: true,
            ticks: { font: { size: 10 } },
            grid: { display: false },
          },
        },
      },
    });
  }

  function renderHeatmapFallback(heatmapData, allMonths) {
    const subcategories = [...new Set(heatmapData.map(e => e.subcategory))];
    const lookup = {};
    let maxVal = 0;
    for (const e of heatmapData) {
      const key = `${e.subcategory}|${e.month}`;
      lookup[key] = e.count;
      if (e.count > maxVal) maxVal = e.count;
    }

    const container = document.getElementById("chartHeatmap").parentNode;
    const table = document.createElement("div");
    table.className = "heatmap-table-wrap";
    let html = '<table class="heatmap-table"><thead><tr><th></th>';
    for (const m of allMonths) html += `<th>${m}</th>`;
    html += "</tr></thead><tbody>";
    for (const s of subcategories) {
      html += `<tr><td class="hm-label">${escapeHtml(s)}</td>`;
      for (const m of allMonths) {
        const v = lookup[`${s}|${m}`] || 0;
        const alpha = maxVal > 0 ? Math.max(0.05, v / maxVal) : 0;
        html += `<td class="hm-cell" style="background:rgba(59,91,219,${alpha})" title="${s} / ${m}: ${v}건">${v || ""}</td>`;
      }
      html += "</tr>";
    }
    html += "</tbody></table>";
    table.innerHTML = html;
    container.style.height = "auto";
    container.innerHTML = "";
    container.appendChild(table);
  }

  // -----------------------------------------------------------------------
  // Section 7: 텍스트 마이닝
  // -----------------------------------------------------------------------
  function renderTextAnalysis(data) {
    const ta = data.text_analysis;

    const kw = ta.keyword_frequency.slice(0, 30);
    createChart("chartKeywords", {
      type: "bar",
      data: {
        labels: kw.map(e => e.word),
        datasets: [{ label: "빈도", data: kw.map(e => e.count), backgroundColor: COLORS.primary }],
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const lenDist = ta.summary_length_distribution;
    const lenOrder = ["~20자", "20~50자", "50~100자", "100~200자", "200자+"];
    const lenLabels = lenOrder.filter(k => lenDist[k] !== undefined);

    createChart("chartLengthDist", {
      type: "pie",
      data: {
        labels: lenLabels,
        datasets: [{ data: lenLabels.map(k => lenDist[k]), backgroundColor: PALETTE }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });

    const avgLen = ta.avg_summary_length_by_subcategory;
    const sortedLen = Object.entries(avgLen).sort((a, b) => b[1] - a[1]);

    createChart("chartAvgLength", {
      type: "bar",
      data: {
        labels: sortedLen.map(e => e[0]),
        datasets: [{ label: "평균 글자 수", data: sortedLen.map(e => e[1]), backgroundColor: COLORS.green }],
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });

    const kwBySub = ta.keyword_by_subcategory;
    const grid = document.getElementById("keywordBySubGrid");
    grid.innerHTML = Object.entries(kwBySub)
      .filter(([, arr]) => arr.length > 0)
      .sort((a, b) => a[0].localeCompare(b[0], "ko"))
      .map(([sub, arr]) => {
        const tags = arr.slice(0, 10).map(e =>
          `<span class="kw-tag">${escapeHtml(e.word)}<span class="kw-count">(${e.count})</span></span>`
        ).join("");
        return `<div class="keyword-sub-card"><h4>${escapeHtml(sub)}</h4><div class="kw-list">${tags}</div></div>`;
      }).join("");

    const topKw = kw.slice(0, 5).map(e => `<strong>${e.word}</strong>(${e.count}회)`).join(", ");
    document.getElementById("insightText").innerHTML =
      `<strong>텍스트 마이닝 인사이트</strong>
      <ul>
        <li>전체 주요 키워드: ${topKw}</li>
        <li>세부분야별 키워드를 통해 각 분야의 핵심 관심사와 트렌드를 파악할 수 있습니다.</li>
        <li>아이디어 요약 평균 길이는 분야에 따라 차이가 있으며, 이는 아이디어 구체성의 지표로 활용 가능합니다.</li>
      </ul>`;
  }

  // -----------------------------------------------------------------------
  // 초기화
  // -----------------------------------------------------------------------
  async function init() {
    try {
      const res = await fetch("/api/analytics");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (data.empty) {
        document.getElementById("meta").textContent = "데이터가 없습니다. 아이디어 목록에서 수집을 먼저 진행해주세요.";
        document.getElementById("loadingOverlay").classList.add("hidden");
        return;
      }

      renderSummary(data);
      renderDistribution(data);
      renderTimeSeries(data);
      renderEngagement(data);
      renderContributors(data);
      renderCrossAnalysis(data);
      renderTextAnalysis(data);

      document.getElementById("loadingOverlay").classList.add("hidden");
    } catch (err) {
      console.error("Analytics load error:", err);
      document.getElementById("meta").textContent = "분석 데이터 로드 실패";
      document.getElementById("loadingOverlay").classList.add("hidden");
    }
  }

  init();
})();
