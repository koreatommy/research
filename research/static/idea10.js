(function () {
  "use strict";

  const fusionGaps = [
    ["ESG + 금융/투자", 25, "hot", "ESG 1,421건과 금융성 키워드 882건이 있지만 교차는 25건으로 낮습니다."],
    ["1인가구 + ESG/환경", 13, "hot", "1인가구 676건, ESG/환경 1,421건 대비 교차는 13건입니다."],
    ["패션 + 지속가능/ESG", 23, "hot", "패션 203건 중 ESG/지속가능 교차는 23건입니다."],
    ["시니어 + 금융/재무", 42, "warm", "시니어 1,435건, 금융성 키워드 882건 대비 교차는 42건입니다."],
    ["로컬 + 뷰티", 45, "warm", "로컬 3,214건, 뷰티 키워드 776건 대비 교차는 45건입니다."],
    ["웰다잉 + AI", 43, "warm", "웰다잉/장례/유산 194건 중 AI 교차는 43건입니다."],
  ];

  const ideas = [
    {
      no: "01",
      title: "상권 기후 지도 (Street Climate OS)",
      subtitle: "소음·냄새·그늘·대기질까지 반영하는 초미세 상권 입지 리스크 스코어",
      tags: [["niche", "프롭테크 167건"], ["trend", "로컬 6,098건"], ["tech", "공간 데이터"]],
      idea: "상권 분석은 보통 유동인구와 매출에 멈추지만, 실제 폐업을 좌우하는 요소는 냄새, 소음, 햇빛, 그늘, 흡연 동선, 쓰레기 배출 시간 같은 미시 환경입니다. 상권 기후 지도는 센서·리뷰·민원·위성 그림자·날씨 데이터를 합쳐 점포 단위의 '장사하기 좋은 시간표'를 만듭니다. 창업자는 계약 전에 냄새 리스크, 점심 피크 그늘, 야간 소음, 배달 접근성을 점수로 보고, 임대인은 개선 리포트를 받아 임대료를 방어합니다.",
      evidence: "프롭테크는 167건으로 저밀도지만 평균 사업화 점수 1위입니다. 로컬은 6,098건으로 수요가 크나 미시 공간 리스크를 다루는 모델은 희소합니다.",
      target: "예비 창업자, 상가 임대인, 프랜차이즈 출점팀, 지자체 상권 활성화 부서",
      metrics: [["독창성", "매우 높음"], ["데이터 장벽", "높음"], ["B2B 수익", "높음"]],
    },
    {
      no: "02",
      title: "빈자리 선물거래소 (Idle Seat Exchange)",
      subtitle: "카페 좌석·학원 교실·미용실 의자·주차면을 15분 단위로 사고파는 로컬 유휴자산 시장",
      tags: [["trend", "로컬 6,098건"], ["trend", "B2B 5,613건"], ["tech", "초단위 예약"]],
      idea: "동네에는 비어 있는 자산이 많습니다. 오전의 술집, 낮의 학원 교실, 비수기 미용실 의자, 비는 주차면, 비는 공유오피스 부스입니다. 이 서비스는 유휴 공간을 15분 단위 상품으로 쪼개 판매합니다. 사용자는 '조용히 통화할 25분', '아이 숙제 봐줄 40분', '촬영용 흰 벽 1시간'처럼 목적 기반으로 예약하고, 가게는 빈 시간을 매출로 바꿉니다.",
      evidence: "로컬 키워드는 3,214건, 로컬 분야는 6,098건입니다. 반면 저밀도 프롭테크와 운영관리의 교차형 로컬 자산 거래 모델은 아직 드뭅니다.",
      target: "동네 카페·학원·미용실·주차장 운영자, 짧은 공간이 필요한 프리랜서·학생·부모",
      metrics: [["시장 신선도", "높음"], ["운영 난도", "중간"], ["네트워크 효과", "높음"]],
    },
    {
      no: "03",
      title: "사장님 그림자 직원 (Shadow Staff AI)",
      subtitle: "자영업자의 리뷰·재고·민원·발주를 밤새 처리하는 AI 운영 대타",
      tags: [["trend", "소상공인 1,009건"], ["trend", "AI 8,194건"], ["niche", "운영관리 1,014건"]],
      idea: "소상공인 AI 도구는 홍보 문구 생성에 치우쳐 있습니다. 그림자 직원은 문 닫은 뒤 사장님 대신 내일 할 일을 처리합니다. 리뷰 답변, 재고 부족 예측, 식자재 발주 초안, 알바 스케줄 충돌, 단골 이탈 알림, 악성 민원 분류를 하나의 야간 리포트로 제공합니다. 핵심은 'AI 챗봇'이 아니라 실제로 사장님의 새벽 노동을 줄이는 운영 대행입니다.",
      evidence: "소상공인·자영업 고객군은 1,009건, B2B 추정은 5,613건입니다. AI 언급은 많지만 운영관리형 소상공인 야간 자동화는 차별화 여지가 큽니다.",
      target: "1~5인 매장 사장님, 프랜차이즈 가맹점, 배달·예약·리뷰를 동시에 관리하는 로컬 사업자",
      metrics: [["반복 매출", "높음"], ["실행성", "높음"], ["차별화", "높음"]],
    },
    {
      no: "04",
      title: "실버 리허설 룸 (Silver Rehearsal Room)",
      subtitle: "시니어가 키오스크·병원·은행·공항 상황을 가상으로 연습하는 생활 시뮬레이터",
      tags: [["trend", "시니어 1,435건"], ["trend", "AI 8,194건"], ["niche", "임팩트 281건"]],
      idea: "시니어 교육은 강의형이 많지만, 실제 어려움은 현장에서 버튼을 잘못 누를까 봐 생기는 공포입니다. 실버 리허설 룸은 키오스크 주문, 병원 접수, 은행 상담, 공항 출국, 택시 호출을 가상 공간에서 반복 연습하게 합니다. 가족은 부모님이 어떤 단계에서 막히는지 리포트를 받고, 프랜차이즈·병원·은행은 고령 고객 UX 테스트 도구로 씁니다.",
      evidence: "시니어 고객군은 1,099건, 시니어 관련 키워드는 1,435건입니다. 임팩트 분야는 281건으로 저밀도이며 시니어 디지털 적응 문제는 사회 가치가 큽니다.",
      target: "60세 이상 시니어, 부모님의 외출 독립성을 돕고 싶은 가족, 은행·병원·프랜차이즈 UX팀",
      metrics: [["사회가치", "매우 높음"], ["B2B 확장", "높음"], ["감성 장벽", "낮음"]],
    },
    {
      no: "05",
      title: "화장대 리필 우체통 (Refill Mailbox Beauty)",
      subtitle: "다 쓴 화장품 용기를 집 앞에서 회수하고 개인 피부 처방으로 리필하는 순환 뷰티 물류",
      tags: [["niche", "뷰티 291건"], ["gap", "로컬+뷰티 45건"], ["trend", "ESG 1,421건"]],
      idea: "뷰티 아이디어는 제품 추천에 몰려 있지만, 화장품 쓰레기와 리필 물류는 아직 비어 있습니다. 사용자가 빈 용기를 우체통형 회수함에 넣으면, 서비스가 세척·검수 후 같은 용기에 맞춤 처방 제품을 리필해 돌려줍니다. 피부 상태, 계절, 지역 날씨에 따라 제형을 조정하고, 브랜드는 리필 탄소절감 데이터를 ESG 리포트로 받습니다.",
      evidence: "뷰티는 291건으로 저밀도이고, 로컬+뷰티 교차는 45건입니다. ESG/환경 키워드는 1,421건으로 충분한 트렌드 신호가 있습니다.",
      target: "민감성 피부 고객, 친환경 뷰티 브랜드, 공동주택·오피스 리필 거점 운영자",
      metrics: [["공백률", "높음"], ["물류 난도", "중간"], ["브랜드 제휴", "높음"]],
    },
    {
      no: "06",
      title: "동네 과잉 예보소 (Surplus Weather)",
      subtitle: "지역 농산물·빵·반찬의 내일 남을 양을 예측해 식당과 소비자에게 선판매하는 플랫폼",
      tags: [["trend", "로컬 6,098건"], ["niche", "농축·수산업 931건"], ["tech", "수요 예측"]],
      idea: "못난이 농산물 판매는 이미 흔합니다. 동네 과잉 예보소는 '이미 남은 것'이 아니라 '내일 남을 것'을 예측합니다. 농가, 베이커리, 반찬가게, 식당의 판매 패턴과 날씨·행사·요일 데이터를 학습해 과잉 가능 품목을 전날 밤 할인 선판매합니다. 소비자는 랜덤 박스를 싸게 받고, 판매자는 폐기 전에 수요를 미리 잠급니다.",
      evidence: "로컬 분야는 6,098건, 농축·수산업은 931건입니다. ESG/환경 교차 수요는 강하지만 예측 기반 선판매 모델은 단순 재고 처리보다 차별적입니다.",
      target: "지역 농가, 동네 베이커리·반찬가게, 식비를 줄이고 싶은 1인가구·가족",
      metrics: [["실행성", "높음"], ["데이터 효과", "높음"], ["마진", "중간"]],
    },
    {
      no: "07",
      title: "반려식물 응급실 (Plant ER)",
      subtitle: "죽어가는 식물을 사진 한 장으로 진단하고 동네 가드너가 구조하는 식물 케어 네트워크",
      tags: [["trend", "생활 3,999건"], ["trend", "로컬 6,098건"], ["tech", "이미지 진단"]],
      idea: "반려동물은 많지만 반려식물은 아직 생활·로컬 틈새입니다. 사용자가 시든 잎 사진을 올리면 AI가 과습, 해충, 햇빛 부족, 분갈이 필요를 진단하고, 동네 가드너나 꽃집이 방문 구조·입원 케어를 제공합니다. 식물을 살리면 '구조 인증서'와 재발 방지 루틴이 생기고, 기업 사무실 식물 관리 B2B로 확장합니다.",
      evidence: "생활은 3,999건으로 과밀이지만, 로컬 서비스와 이미지 진단을 결합한 미시 카테고리는 차별화 가능합니다. 로컬 키워드 3,214건도 수요 기반입니다.",
      target: "식물을 자주 죽이는 1인가구·직장인, 동네 꽃집·가드너, 사무실 식물 관리 업체",
      metrics: [["기발함", "높음"], ["진입 장벽", "낮음"], ["로컬 확장", "높음"]],
    },
    {
      no: "08",
      title: "미래 민원 리허설 (Civic Pre-Mortem)",
      subtitle: "가게·축제·건축 프로젝트가 생기기 전 예상 민원을 시뮬레이션하는 B2G/B2B 서비스",
      tags: [["trend", "B2G 577건"], ["niche", "프롭테크 167건"], ["tech", "민원 예측"]],
      idea: "창업자는 오픈 후 민원을 맞고 나서야 문제를 압니다. 미래 민원 리허설은 위치, 업종, 영업시간, 소음, 냄새, 주차, 쓰레기 배출 동선을 입력하면 예상 민원 지도를 미리 만듭니다. 지자체는 허가·축제 기획 전에 갈등 가능성을 보고, 사업자는 방음·환기·동선 개선안을 계약 전에 반영합니다.",
      evidence: "B2G 추정은 577건으로 작지만 명확한 구매자가 있습니다. 프롭테크 167건과 로컬 6,098건 사이의 갈등 예방 영역은 독특한 공백입니다.",
      target: "지자체, 축제 기획사, 상가 창업자, 프랜차이즈 출점팀, 부동산 개발사",
      metrics: [["공공성", "높음"], ["데이터 장벽", "높음"], ["객단가", "높음"]],
    },
    {
      no: "09",
      title: "장바구니 영양 극장 (Grocery Theatre)",
      subtitle: "영수증 속 식습관을 가족 캐릭터 드라마로 보여주는 행동교정 구독 서비스",
      tags: [["trend", "건강·케어 3,526건"], ["trend", "맞춤형 1,588회"], ["tech", "영수증 분석"]],
      idea: "건강 앱은 숫자와 그래프가 많아 금방 지칩니다. 장바구니 영양 극장은 마트 영수증과 배달 주문을 분석해 가족의 식습관을 캐릭터 드라마로 보여줍니다. '나트륨 왕국에 납치된 아빠', '채소 행성 탈출기'처럼 주간 에피소드를 만들고, 다음 장보기 미션을 게임처럼 제안합니다. 보험사·마트·학교 급식 교육과 제휴할 수 있습니다.",
      evidence: "건강·의료·케어 문제유형은 3,526건, 맞춤형 키워드는 1,588회로 강합니다. 그러나 건강 데이터의 표현 방식을 엔터테인먼트화한 접근은 희소합니다.",
      target: "아이 있는 가족, 건강검진 후 식습관 개선이 필요한 직장인, 마트·보험사·학교",
      metrics: [["재미 요소", "매우 높음"], ["제휴성", "높음"], ["개인정보 장벽", "중간"]],
    },
    {
      no: "10",
      title: "규제 괴물 도감 (Regulation Monster Dex)",
      subtitle: "업종별 숨어 있는 인허가·표시·세무 리스크를 캐릭터 도감처럼 잡아주는 창업 규제 게임",
      tags: [["trend", "소상공인 1,009건"], ["trend", "B2B 5,613건"], ["niche", "재무 34건"]],
      idea: "창업 실패의 상당수는 아이디어가 아니라 몰랐던 규제와 세무에서 옵니다. 규제 괴물 도감은 업종·지역·판매 채널을 입력하면 숨어 있는 인허가, 표시광고, 원산지, 개인정보, 세금 리스크를 괴물 캐릭터로 보여주고 하나씩 퇴치하게 합니다. 회계사·노무사·행정사 상담은 '보스전'처럼 연결하고, 완료하면 투자자·프랜차이즈 본사에 제출 가능한 준법 리포트를 발급합니다.",
      evidence: "재무는 34건으로 최저밀도이고 B2B 추정은 5,613건입니다. 소상공인 1,009건 수요와 규제·재무 공백을 결합한 실행형 도구입니다.",
      target: "예비 창업자, 온라인 셀러, 프랜차이즈 가맹 희망자, 창업 교육기관",
      metrics: [["차별화", "매우 높음"], ["수익화", "높음"], ["전문가 제휴", "높음"]],
    },
  ];

  function fmt(n) {
    return Number(n || 0).toLocaleString();
  }

  function pct(part, total) {
    if (!total) return "0.0";
    return ((part / total) * 100).toFixed(1);
  }

  function esc(s) {
    return String(s || "").replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  function setText(selector, text) {
    const el = document.querySelector(selector);
    if (el) el.textContent = text;
  }

  function replaceSummaryCards(a, insight) {
    const total = a.meta.total;
    const ai = insight.quantitative.ai_usage.yes;
    const b2b = insight.quantitative.b2x.B2B || 0;
    const tech = a.division_distribution["일반/기술"] || 0;
    const local = a.division_distribution["로컬"] || 0;
    const sparse = insight.strategic.sparse_subcategories || [];
    const grid = document.querySelector(".data-grid");
    if (!grid) return;
    grid.innerHTML = [
      ["총 아이디어 수", fmt(total), ""],
      [`AI 언급 (${pct(ai, total)}%)`, fmt(ai), ""],
      [`B2B 추정 (${pct(b2b, total)}%)`, fmt(b2b), ""],
      [`최저밀도: ${sparse[0]?.subcategory || "재무"}`, `${fmt(sparse[0]?.count || 0)}건`, "accent"],
      [`일반/기술 분야 (${pct(tech, total)}%)`, fmt(tech), ""],
      [`로컬 분야 (${pct(local, total)}%)`, fmt(local), ""],
    ].map(([label, value, cls]) =>
      `<div class="data-card ${esc(cls)}"><div class="data-value">${esc(value)}</div><div class="data-label">${esc(label)}</div></div>`
    ).join("");
  }

  function replaceHero(a, insight) {
    const total = a.meta.total;
    const ai = insight.quantitative.ai_usage.yes;
    const sparseCount = (insight.strategic.sparse_subcategories || []).length;
    const values = document.querySelectorAll(".hero-stat-value");
    const labels = document.querySelectorAll(".hero-stat-label");
    const pairs = [
      [fmt(total), "전수 분석 아이디어"],
      [String(a.meta.subcategory_count || 22), "세부 분야"],
      [fmt(ai), `AI 언급 아이디어 (${pct(ai, total)}%)`],
      [String(sparseCount), "저밀도 기회 분야"],
    ];
    pairs.forEach(([v, l], idx) => {
      if (values[idx]) values[idx].textContent = v;
      if (labels[idx]) labels[idx].textContent = l;
    });
    setText(".container section .section-subtitle", `${fmt(total)}건 전수 데이터 기반 정량 분석`);
  }

  function renderKeywordCards(a, insight) {
    const ai = insight.quantitative.ai_usage.yes;
    const top = a.text_analysis.keyword_frequency || [];
    const topMap = Object.fromEntries(top.map(x => [x.word, x.count]));
    const social = insight.qualitative.social_idea_count || 0;
    const local = insight.qualitative.local_idea_count || 0;
    const customer = insight.quantitative.customer_segment || {};
    const cards = [
      ["메가 트렌드", [
        ["AI/인공지능", ai], ["맞춤형", topMap["맞춤형"]], ["스마트", topMap["스마트"]], ["실시간", topMap["실시간"]],
      ]],
      ["고객/시장 신호", [
        ["시니어", customer["시니어"]], ["소상공인", customer["소상공인·자영업"]], ["학생·청년", customer["학생·청년"]], ["기업/B2B", customer["기업·B2B고객"]],
      ]],
      ["전략 키워드", [
        ["사회·임팩트", social], ["로컬", local], ["브랜드", topMap["브랜드"]], ["데이터", topMap["데이터"]],
      ]],
    ];
    const max = Math.max(...cards.flatMap(([, rows]) => rows.map(([, n]) => n || 0)), 1);
    const grid = document.querySelector(".keyword-grid");
    if (!grid) return;
    grid.innerHTML = cards.map(([title, rows]) =>
      `<div class="keyword-card"><div class="keyword-title">${esc(title)}</div>${
        rows.map(([name, count]) => {
          const width = Math.max(6, Math.round((Number(count || 0) / max) * 100));
          return `<div class="keyword-bar"><span class="keyword-name">${esc(name)}</span><div class="keyword-progress"><div class="keyword-progress-fill" style="width:${width}%"></div></div><span class="keyword-count">${fmt(count)}건</span></div>`;
        }).join("")
      }</div>`
    ).join("");
  }

  function renderGaps(insight, total) {
    const [opp, sat] = document.querySelectorAll(".gap-card");
    const sparse = insight.strategic.sparse_subcategories || [];
    const crowded = insight.strategic.crowded_subcategories || [];
    if (opp) {
      opp.querySelector(".gap-title").textContent = "블루오션 저밀도 시장";
      opp.querySelectorAll(".gap-item").forEach(x => x.remove());
      opp.insertAdjacentHTML("beforeend", sparse.map(x =>
        `<div class="gap-item"><span class="gap-name">${esc(x.subcategory)}</span><span class="gap-count">${fmt(x.count)}건 (${pct(x.count, total)}%) · 평균 ♥ ${x.avg_likes}</span></div>`
      ).join(""));
    }
    if (sat) {
      sat.querySelector(".gap-title").textContent = "레드오션 과밀 시장";
      sat.querySelectorAll(".gap-item").forEach(x => x.remove());
      sat.insertAdjacentHTML("beforeend", crowded.map(x =>
        `<div class="gap-item"><span class="gap-name">${esc(x.subcategory)}</span><span class="gap-count">${fmt(x.count)}건 (${pct(x.count, total)}%)</span></div>`
      ).join(""));
    }
  }

  function renderFusionTable() {
    const tbody = document.querySelector(".fusion-table tbody");
    if (!tbody) return;
    tbody.innerHTML = fusionGaps.map(([name, count, level, meaning]) =>
      `<tr><td><strong>${esc(name)}</strong></td><td>${fmt(count)}건</td><td><span class="fusion-badge ${level}">${level === "hot" ? "극심한 공백" : "공백"}</span></td><td>${esc(meaning)}</td></tr>`
    ).join("");
  }

  function renderIdeas() {
    const container = document.querySelector(".ideas-container");
    if (!container) return;
    container.innerHTML = ideas.map(idea =>
      `<div class="idea-card">
        <div class="idea-header">
          <div class="idea-number">${idea.no}</div>
          <div class="idea-tags">${idea.tags.map(([cls, text]) => `<span class="idea-tag ${cls}">${esc(text)}</span>`).join("")}</div>
          <h3 class="idea-title">${esc(idea.title)}</h3>
          <p class="idea-subtitle">${esc(idea.subtitle)}</p>
        </div>
        <div class="idea-body">
          <div class="idea-section"><div class="idea-section-title">핵심 아이디어</div><p>${esc(idea.idea)}</p></div>
          <div class="idea-evidence"><div class="idea-evidence-title">데이터 근거</div><p>${esc(idea.evidence)}</p></div>
          <div class="idea-section"><div class="idea-section-title">타겟 고객</div><p>${esc(idea.target)}</p></div>
          <div class="idea-metrics">${idea.metrics.map(([label, value], idx) =>
            `<div class="metric"><div class="metric-value">${esc(value)}</div><div class="metric-label">${esc(label)}</div><div class="metric-bar"><div class="metric-bar-fill" style="width:${[92, 72, 86][idx]}%"></div></div></div>`
          ).join("")}</div>
        </div>
      </div>`
    ).join("");
  }

  function renderCharts(a, insight) {
    const crowded = insight.strategic.crowded_subcategories || [];
    const sparse = insight.strategic.sparse_subcategories || [];
    const saturatedCanvas = document.getElementById("saturatedChart");
    const nicheCanvas = document.getElementById("nicheChart");
    if (window.Chart && saturatedCanvas) {
      Chart.getChart(saturatedCanvas)?.destroy();
      new Chart(saturatedCanvas, {
        type: "bar",
        data: {
          labels: crowded.map(x => x.subcategory),
          datasets: [{ label: "아이디어 수", data: crowded.map(x => x.count), backgroundColor: "rgba(233, 69, 96, 0.75)", borderRadius: 6 }],
        },
        options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } },
      });
    }
    if (window.Chart && nicheCanvas) {
      Chart.getChart(nicheCanvas)?.destroy();
      new Chart(nicheCanvas, {
        type: "doughnut",
        data: {
          labels: sparse.map(x => `${x.subcategory} (${fmt(x.count)})`),
          datasets: [{ data: sparse.map(x => x.count), backgroundColor: ["#00d9ff", "#0f3460", "#16213e", "#1a1a2e", "#e94560"] }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" } }, cutout: "55%" },
      });
    }
  }

  function replaceMethodology(a, insight) {
    const total = a.meta.total;
    const items = document.querySelectorAll(".methodology-item p");
    const texts = [
      `modoo.or.kr의 최신 ${fmt(total)}건 아이디어를 파싱해 분야 분포, 좋아요, 참여자, 시계열, 텍스트 키워드를 집계했습니다.`,
      "Raw data의 분야·키워드 분포와 Insight의 고객군·문제유형·사업화 점수를 함께 사용해 공백 조합을 찾았습니다.",
      "각 후보는 최신 키워드 조합 건수와 과밀/저밀도 분야를 대조해 기존 아이디어와의 중복 가능성을 낮췄습니다.",
      "저밀도 분야(재무·프롭테크·패션·임팩트·뷰티)와 강한 수요 신호(AI, 시니어, 로컬, B2B)를 교차해 10개 콘셉트를 재선정했습니다.",
    ];
    texts.forEach((t, idx) => { if (items[idx]) items[idx].textContent = t; });

    const conclusion = document.querySelector(".conclusion");
    if (conclusion) {
      const crowded = insight.strategic.crowded_subcategories?.[0];
      const sparse = insight.strategic.sparse_subcategories || [];
      conclusion.innerHTML = `<h2>결론 및 전략적 제언</h2>
        <p>${fmt(total)}건 최신 분석 결과, <strong>${esc(crowded?.subcategory || "IT")} 분야(${fmt(crowded?.count)}건)</strong> 중심 과밀이 뚜렷합니다. 반면 <strong>${sparse.map(x => `${esc(x.subcategory)}(${fmt(x.count)}건)`).join(", ")}</strong>은 낮은 경쟁 밀도의 기회 영역입니다. 따라서 단순 AI 앱보다 저밀도 분야와 명확한 고객/수익 모델을 결합한 아이디어가 유리합니다.</p>
        <ul class="conclusion-list">
          <li><strong>최우선 기회:</strong> ESG+금융, 1인가구+ESG, 패션+ESG처럼 교차 건수가 낮은 조합</li>
          <li><strong>B2B 기회:</strong> B2B 추정 ${fmt(insight.quantitative.b2x.B2B || 0)}건 흐름을 활용한 SaaS·리포팅 모델</li>
          <li><strong>고객 명확성:</strong> 시니어, 소상공인, 기업 고객처럼 명시 고객군이 있는 모델 우선</li>
          <li><strong>차별화 방향:</strong> 과밀 IT 영역은 권리·정산·컴플라이언스 같은 인프라 레이어로 접근</li>
        </ul>`;
    }
  }

  function replaceFooter(a) {
    const footer = document.querySelector("footer");
    if (!footer) return;
    const date = a.meta.crawled_at ? String(a.meta.crawled_at).slice(0, 10) : "-";
    footer.innerHTML = `<p>본 보고서는 <a href="https://www.modoo.or.kr/idea/list" target="_blank">modoo.or.kr</a> 최신 전수 데이터(${fmt(a.meta.total)}건)를 Raw data 분석 및 Insight 결과와 결합해 생성되었습니다.</p><p style="margin-top: 10px;">분석 시점: ${date} · 데이터 기준: /data/analytics.json, /data/insight.json</p>`;
  }

  async function init() {
    try {
      const [analyticsRes, insightRes] = await Promise.all([
        fetch("/data/analytics.json"),
        fetch("/data/insight.json"),
      ]);
      if (!analyticsRes.ok || !insightRes.ok) return;
      const [analytics, insight] = await Promise.all([analyticsRes.json(), insightRes.json()]);
      if (analytics.empty || insight.empty) return;

      replaceHero(analytics, insight);
      replaceSummaryCards(analytics, insight);
      renderKeywordCards(analytics, insight);
      renderGaps(insight, analytics.meta.total);
      renderFusionTable();
      renderIdeas();
      renderCharts(analytics, insight);
      replaceMethodology(analytics, insight);
      replaceFooter(analytics);
    } catch (e) {
      console.error("idea10 update failed", e);
    }
  }

  init();
})();
