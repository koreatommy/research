/**
 * 정적 배포용: /data/ideas.json 한 번 로드 후 modoo_filters.filter_ideas 규칙과 동일하게 필터·페이지네이션.
 */
(function () {
  "use strict";

  const DATA_URL = "/data/ideas.json";

  const FALLBACK_SUBCATEGORIES = {
    "일반/기술": [
      "IT", "교육", "금융", "운영관리", "네트워킹", "농축·수산업",
      "라이프스타일", "마케팅/PR", "모빌리티", "미디어/엔터테인먼트",
      "바이오/의료", "에너지/자원", "유통/물류", "임팩트", "재무",
      "프롭테크", "하드웨어", "기타",
    ],
    로컬: ["패션", "F&B", "뷰티", "생활"],
  };

  let ideasPayload = null;
  let allIdeas = [];

  let currentPage = 1;
  let pageSize = 12;
  let totalPages = 1;
  let rawTotalAll = 0;
  let subcategoriesByDivision = {};

  const metaEl = document.getElementById("meta");
  const divisionSelect = document.getElementById("divisionSelect");
  const subcategorySelect = document.getElementById("subcategorySelect");
  const keywordInput = document.getElementById("keywordInput");
  const searchBtn = document.getElementById("searchBtn");
  const resetFilterBtn = document.getElementById("resetFilterBtn");
  const filterNote = document.getElementById("filterNote");
  const filterResultCount = document.getElementById("filterResultCount");
  const tbody = document.querySelector("#ideasTable tbody");
  const pageSizeSelect = document.getElementById("pageSizeSelect");

  const pageInfo = document.getElementById("pageInfo");
  const pageInfo2 = document.getElementById("pageInfo2");
  const firstBtn = document.getElementById("firstBtn");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const lastBtn = document.getElementById("lastBtn");
  const firstBtn2 = document.getElementById("firstBtn2");
  const prevBtn2 = document.getElementById("prevBtn2");
  const nextBtn2 = document.getElementById("nextBtn2");
  const lastBtn2 = document.getElementById("lastBtn2");

  function ideaText(idea) {
    const summary = (idea.summary || "").toLowerCase();
    const tags = idea.tags || [];
    const tagPart = tags.map((t) => String(t).toLowerCase()).join(" ");
    return `${summary} ${tagPart}`;
  }

  function ideaPassesFilters(idea, division, subcategory, q) {
    const div = idea.division || "";
    if (division && div !== division) return false;
    if (q) {
      const needle = q.trim().toLowerCase();
      if (needle && !ideaText(idea).includes(needle)) return false;
    }
    if (subcategory) {
      const ideaSub = idea.subcategory || "";
      if (ideaSub !== subcategory) return false;
    }
    return true;
  }

  function filterIdeas(ideas, division, subcategory, q) {
    return ideas.filter((i) =>
      ideaPassesFilters(i, division, subcategory, q)
    );
  }

  function buildSubcategoriesFromIdeas(ideas) {
    const subcategoriesByDivision = {};
    for (const idea of ideas) {
      const div = idea.division;
      const sub = idea.subcategory;
      if (div && sub) {
        if (!subcategoriesByDivision[div]) subcategoriesByDivision[div] = [];
        if (!subcategoriesByDivision[div].includes(sub)) {
          subcategoriesByDivision[div].push(sub);
        }
      }
    }
    return subcategoriesByDivision;
  }

  function applyMetaFromPayload(payload) {
    const ideas = payload.ideas || [];
    allIdeas = ideas;
    rawTotalAll =
      typeof payload.total === "number" ? payload.total : ideas.length;
    window._crawledDate = payload.crawled_at
      ? String(payload.crawled_at).slice(0, 10)
      : "-";

    let subMap = buildSubcategoriesFromIdeas(ideas);
    if (Object.keys(subMap).length === 0) {
      subMap = {
        "일반/기술": [...FALLBACK_SUBCATEGORIES["일반/기술"]],
        로컬: [...FALLBACK_SUBCATEGORIES.로컬],
      };
    }
    subcategoriesByDivision = subMap;

    const divisions = [
      ...new Set(ideas.map((i) => i.division).filter(Boolean)),
    ].sort();

    if (rawTotalAll) {
      metaEl.textContent = `전체 ${rawTotalAll.toLocaleString()}건 · 수집일: ${window._crawledDate}`;
    } else {
      metaEl.textContent =
        "데이터가 없습니다. 로컬에서 수집 후 export_for_research.py로 data/ideas.json을 갱신하세요.";
    }

    divisionSelect.innerHTML = '<option value="">전체</option>';
    for (const d of divisions) {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      divisionSelect.appendChild(opt);
    }
    rebuildSubcategoryOptions();
    filterNote.classList.toggle("hidden", !rawTotalAll);
  }

  function updateMetaLine(dataIdeas) {
    const date = window._crawledDate || "-";
    const base = rawTotalAll
      ? `전체 ${rawTotalAll.toLocaleString()}건 · 수집일: ${date}`
      : metaEl.textContent || "";
    if (!dataIdeas || !dataIdeas.filters) {
      metaEl.textContent = base;
      return;
    }
    const f = dataIdeas.filters;
    const hasFilter = f.division || f.subcategory || f.q;
    if (hasFilter && typeof dataIdeas.raw_total === "number") {
      const n = dataIdeas.total ?? 0;
      metaEl.textContent = `${base} · 조건 결과 ${n.toLocaleString()}건`;
    } else {
      metaEl.textContent = base;
    }
  }

  function updateFilterResultCount(dataIdeas) {
    const selectedSubcategory = subcategorySelect.value;
    if (
      !selectedSubcategory ||
      !dataIdeas ||
      typeof dataIdeas.total !== "number"
    ) {
      filterResultCount.textContent = "";
      filterResultCount.classList.add("hidden");
      return;
    }
    filterResultCount.textContent = `세부분야 '${selectedSubcategory}' 검색 결과: ${dataIdeas.total.toLocaleString()}건`;
    filterResultCount.classList.remove("hidden");
  }

  function rebuildSubcategoryOptions() {
    const div = divisionSelect.value;
    subcategorySelect.innerHTML = "";
    const allOpt = document.createElement("option");
    allOpt.value = "";
    allOpt.textContent = "세부 전체";
    subcategorySelect.appendChild(allOpt);

    let options = [];
    if (div) {
      options = subcategoriesByDivision[div] || [];
    } else {
      const merged = [];
      for (const list of Object.values(subcategoriesByDivision)) {
        for (const name of list) {
          if (!merged.includes(name)) merged.push(name);
        }
      }
      options = merged;
    }

    if (!options.length) {
      subcategorySelect.disabled = true;
      allOpt.textContent = div
        ? "해당 대분야에 세부 목록 없음"
        : "세부 목록 없음";
      return;
    }

    subcategorySelect.disabled = false;
    for (const name of options) {
      const o = document.createElement("option");
      o.value = name;
      o.textContent = name;
      subcategorySelect.appendChild(o);
    }
  }

  function currentFilterParams() {
    const div = divisionSelect.value.trim() || null;
    const sub = subcategorySelect.value.trim() || null;
    const kw = keywordInput.value.trim() || null;
    return {
      division: div,
      subcategory: sub,
      q: kw,
    };
  }

  function loadIdeasLocal() {
    const { division, subcategory, q } = currentFilterParams();
    const filtered = filterIdeas(allIdeas, division, subcategory, q);
    const total = filtered.length;
    const raw_total = allIdeas.length;
    totalPages = total ? Math.max(1, Math.ceil(total / pageSize)) : 1;
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const items = filtered.slice(start, end);

    return {
      items,
      page: currentPage,
      page_size: pageSize,
      total,
      total_pages: totalPages,
      raw_total,
      filters: { division, subcategory, q },
    };
  }

  function renderIdeas() {
    tbody.innerHTML =
      '<tr><td colspan="7" class="loading">로딩 중...</td></tr>';
    try {
      if (!ideasPayload) {
        tbody.innerHTML =
          '<tr><td colspan="7" class="error">데이터가 로드되지 않았습니다.</td></tr>';
        return;
      }
      const data = loadIdeasLocal();
      totalPages = data.total_pages || 1;
      currentPage = data.page || currentPage;
      renderTable(data.items);
      updateControls();
      updateMetaLine(data);
      updateFilterResultCount(data);
    } catch {
      tbody.innerHTML =
        '<tr><td colspan="7" class="error">데이터 처리 실패</td></tr>';
      updateFilterResultCount(null);
    }
  }

  function renderTable(items) {
    if (!items || items.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="7" class="empty">표시할 데이터가 없습니다.</td></tr>';
      return;
    }
    tbody.innerHTML = items
      .map(
        (i) => `
        <tr>
          <td>${i.index}</td>
          <td class="summary">${escapeHtml(i.summary)}</td>
          <td><span class="badge ${badgeClass(i.division)}">${escapeHtml(i.division)}</span></td>
          <td class="subcategory">${escapeHtml(i.subcategory || "")}</td>
          <td>${escapeHtml(i.nickname)}</td>
          <td class="likes">&#x2665; ${i.likes}</td>
          <td class="date">${(i.created_at || "").slice(0, 10)}</td>
        </tr>
      `
      )
      .join("");
  }

  function updateControls() {
    const info = `${currentPage} / ${totalPages}`;
    pageInfo.textContent = info;
    pageInfo2.textContent = info;

    const isFirst = currentPage <= 1;
    const isLast = currentPage >= totalPages;

    firstBtn.disabled = isFirst;
    prevBtn.disabled = isFirst;
    nextBtn.disabled = isLast;
    lastBtn.disabled = isLast;
    firstBtn2.disabled = isFirst;
    prevBtn2.disabled = isFirst;
    nextBtn2.disabled = isLast;
    lastBtn2.disabled = isLast;
  }

  function badgeClass(div) {
    if (div === "일반/기술") return "badge-blue";
    if (div === "로컬") return "badge-green";
    if (div === "사회적") return "badge-purple";
    if (div === "그린") return "badge-teal";
    if (div === "문화") return "badge-orange";
    return "badge-gray";
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>"']/g, (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c])
    );
  }

  function goFirst() {
    currentPage = 1;
    renderIdeas();
  }
  function goPrev() {
    if (currentPage > 1) {
      currentPage--;
      renderIdeas();
    }
  }
  function goNext() {
    if (currentPage < totalPages) {
      currentPage++;
      renderIdeas();
    }
  }
  function goLast() {
    currentPage = totalPages;
    renderIdeas();
  }

  firstBtn.addEventListener("click", goFirst);
  prevBtn.addEventListener("click", goPrev);
  nextBtn.addEventListener("click", goNext);
  lastBtn.addEventListener("click", goLast);
  firstBtn2.addEventListener("click", goFirst);
  prevBtn2.addEventListener("click", goPrev);
  nextBtn2.addEventListener("click", goNext);
  lastBtn2.addEventListener("click", goLast);

  pageSizeSelect.addEventListener("change", () => {
    pageSize = parseInt(pageSizeSelect.value, 10);
    currentPage = 1;
    renderIdeas();
  });

  divisionSelect.addEventListener("change", () => {
    rebuildSubcategoryOptions();
    currentPage = 1;
    renderIdeas();
  });

  subcategorySelect.addEventListener("change", () => {
    currentPage = 1;
    renderIdeas();
  });

  keywordInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      currentPage = 1;
      renderIdeas();
    }
  });

  searchBtn.addEventListener("click", () => {
    currentPage = 1;
    renderIdeas();
  });

  resetFilterBtn.addEventListener("click", () => {
    divisionSelect.value = "";
    keywordInput.value = "";
    rebuildSubcategoryOptions();
    updateFilterResultCount(null);
    currentPage = 1;
    renderIdeas();
    const date = window._crawledDate || "-";
    if (rawTotalAll) {
      metaEl.textContent = `전체 ${rawTotalAll.toLocaleString()}건 · 수집일: ${date}`;
    }
  });

  async function init() {
    try {
      const res = await fetch(DATA_URL);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      ideasPayload = await res.json();
      applyMetaFromPayload(ideasPayload);
      renderIdeas();
    } catch (e) {
      console.error(e);
      metaEl.textContent = "데이터 로드 실패 (/data/ideas.json)";
      tbody.innerHTML =
        '<tr><td colspan="7" class="error">/data/ideas.json 을 불러올 수 없습니다.</td></tr>';
    }
  }

  init();
})();
