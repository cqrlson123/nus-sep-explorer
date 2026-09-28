(function () {
  "use strict";

  const STORAGE_KEY = "sepExplorer.shortlist.v1";
  const TARGET_TERM = "AY2027/2028 Semester 1";

  let DATA = null;
  let selectedUniName = null;
  let activeTab = "all";
  let courseApprovalFilter = "";

  const el = {
    search: document.getElementById("search"),
    courseSearch: document.getElementById("courseSearch"),
    regionFilter: document.getElementById("regionFilter"),
    countryFilter: document.getElementById("countryFilter"),
    approvalFilter: document.getElementById("approvalFilter"),
    sortBy: document.getElementById("sortBy"),
    shortlistOnly: document.getElementById("shortlistOnly"),
    resetFilters: document.getElementById("resetFilters"),
    metaBox: document.getElementById("metaBox"),
    resultCount: document.getElementById("resultCount"),
    universityList: document.getElementById("universityList"),
    detailEmpty: document.getElementById("detailEmpty"),
    detailContent: document.getElementById("detailContent"),
    shortlistCount: document.getElementById("shortlistCount"),
    tabs: document.querySelectorAll(".tab"),
  };

  // ---------- shortlist (localStorage) ----------
  function loadShortlist() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? new Set(JSON.parse(raw)) : new Set();
    } catch (e) {
      return new Set();
    }
  }
  function saveShortlist(set) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
    } catch (e) {
      /* ignore (private mode / storage blocked) */
    }
  }
  let shortlist = loadShortlist();

  function toggleShortlist(name) {
    if (shortlist.has(name)) shortlist.delete(name);
    else shortlist.add(name);
    saveShortlist(shortlist);
    render();
    if (selectedUniName === name) renderDetail(findUni(name));
  }

  // ---------- helpers ----------
  function findUni(name) {
    return DATA.universities.find((u) => u.name === name);
  }

  function searchLink(query) {
    return "https://www.google.com/search?q=" + encodeURIComponent(query);
  }

  function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function courseMatches(course, q) {
    const hay = [
      ...course.puCourses.map((c) => c.code + " " + (c.title || "")),
      ...course.nusCourses.map((c) => c.code + " " + (c.title || "")),
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  }

  // ---------- filtering ----------
  function getFilteredUniversities() {
    const nameQ = el.search.value.trim().toLowerCase();
    const courseQ = el.courseSearch.value.trim().toLowerCase();
    const region = el.regionFilter.value;
    const country = el.countryFilter.value;
    const approval = el.approvalFilter.value;

    let list = DATA.universities.filter((u) => {
      if (activeTab === "shortlist" && !shortlist.has(u.name)) return false;
      if (nameQ && !u.name.toLowerCase().includes(nameQ)) return false;
      if (region && u.region !== region) return false;
      if (country && u.country !== country) return false;
      if (approval === "hasApproved" && u.approvedCount === 0) return false;
      if (approval === "noneApproved" && u.approvedCount > 0) return false;
      if (courseQ && !u.courses.some((c) => courseMatches(c, courseQ))) return false;
      return true;
    });

    const sortBy = el.sortBy.value;
    if (sortBy === "mappings") {
      list = list.slice().sort((a, b) => b.totalMappings - a.totalMappings || a.name.localeCompare(b.name));
    } else if (sortBy === "approved") {
      list = list.slice().sort((a, b) => b.approvedCount - a.approvedCount || a.name.localeCompare(b.name));
    } else {
      list = list.slice().sort((a, b) => a.name.localeCompare(b.name));
    }
    return list;
  }

  // ---------- rendering: filters ----------
  function populateFilterOptions() {
    const regions = [...new Set(DATA.universities.map((u) => u.region))].sort();
    const countries = [...new Set(DATA.universities.map((u) => u.country))].sort();

    el.regionFilter.innerHTML =
      '<option value="">All regions</option>' +
      regions.map((r) => `<option value="${escapeHtml(r)}">${escapeHtml(r)}</option>`).join("");

    el.countryFilter.innerHTML =
      '<option value="">All countries</option>' +
      countries.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");

    el.metaBox.innerHTML = `
      ${DATA.meta.totalUniversities} partner universities &middot; ${DATA.meta.totalMappingRows.toLocaleString()} course mappings<br/>
      Faculty scope: ${escapeHtml(DATA.meta.faculties.join(", "))}<br/>
      Source: ${escapeHtml(DATA.meta.generatedFrom)}
    `;
  }

  // ---------- rendering: list ----------
  function render() {
    const list = getFilteredUniversities();
    el.resultCount.textContent = `${list.length} of ${DATA.universities.length} universities`;
    el.shortlistCount.textContent = shortlist.size;

    if (list.length === 0) {
      el.universityList.innerHTML = `<li class="empty-msg">No universities match these filters.</li>`;
      return;
    }

    el.universityList.innerHTML = list
      .map((u) => {
        const isSel = u.name === selectedUniName;
        const isStar = shortlist.has(u.name);
        return `
        <li class="uni-row ${isSel ? "selected" : ""}" data-name="${escapeHtml(u.name)}">
          <button class="star ${isStar ? "on" : ""}" data-star="${escapeHtml(u.name)}" title="Toggle shortlist" aria-label="Toggle shortlist">${isStar ? "★" : "☆"}</button>
          <div class="uni-info">
            <div class="uni-name">${escapeHtml(u.name)}</div>
            <div class="uni-sub">${escapeHtml(u.country)}${u.region !== "Unknown" ? " · " + escapeHtml(u.region) : ""}</div>
            <div class="badges">
              <span class="badge approved">${u.approvedCount} pre-approved</span>
              ${u.totalMappings ? `<span class="badge unspecified">${u.totalMappings} total mapping${u.totalMappings === 1 ? "" : "s"}</span>` : ""}
            </div>
          </div>
        </li>`;
      })
      .join("");
  }

  // ---------- rendering: detail ----------
  function renderDetail(u) {
    if (!u) {
      el.detailEmpty.hidden = false;
      el.detailContent.hidden = true;
      return;
    }
    el.detailEmpty.hidden = true;
    el.detailContent.hidden = false;

    const isStar = shortlist.has(u.name);
    const officialSiteQuery = `${u.name} official website`;
    const calendarQuery = `${u.name} academic calendar ${TARGET_TERM} exchange semester dates`;
    const admissionsQuery = `${u.name} international exchange student incoming NUS`;

    el.detailContent.innerHTML = `
      <div class="detail-head">
        <div>
          <h2>${escapeHtml(u.name)}</h2>
          <div class="country-line">${escapeHtml(u.country)}${u.region !== "Unknown" ? " · " + escapeHtml(u.region) : ""}</div>
        </div>
        <button class="star-btn ${isStar ? "on" : ""}" id="detailStarBtn">${isStar ? "★ Shortlisted" : "☆ Add to shortlist"}</button>
      </div>

      <div class="stat-row">
        <div class="stat"><div class="num">${u.totalMappings}</div><div class="lbl">Total course mappings on file</div></div>
        <div class="stat"><div class="num">${u.approvedCount}</div><div class="lbl">Marked pre-approved</div></div>
        <div class="stat"><div class="num">${u.notApprovedCount}</div><div class="lbl">Marked not approved</div></div>
        <div class="stat"><div class="num">${u.unspecifiedCount}</div><div class="lbl">Status unspecified</div></div>
      </div>

      <div class="link-row">
        <a class="link-btn" target="_blank" rel="noopener" href="${searchLink(officialSiteQuery)}">🔗 Find official website</a>
        <a class="link-btn" target="_blank" rel="noopener" href="${searchLink(calendarQuery)}">🗓 Look up academic calendar (${TARGET_TERM})</a>
        <a class="link-btn" target="_blank" rel="noopener" href="${searchLink(admissionsQuery)}">✈️ Incoming exchange / SEP info</a>
      </div>
      <p class="link-note">
        These open a web search rather than a guessed direct link, since exact URLs and AY2027/28 calendar pages
        aren't reliably knowable in advance — most partner universities haven't published that far ahead yet.
      </p>

      <div class="section-title">Course mappings (${u.courses.length})</div>
      <div class="course-filter-row">
        <select id="detailApprovalFilter">
          <option value="">All statuses</option>
          <option value="yes">Pre-approved only</option>
          <option value="no">Not approved only</option>
          <option value="unspecified">Unspecified only</option>
        </select>
      </div>
      <div id="mappingTableWrap"></div>
    `;

    document.getElementById("detailStarBtn").addEventListener("click", () => toggleShortlist(u.name));

    const filterSelect = document.getElementById("detailApprovalFilter");
    filterSelect.value = courseApprovalFilter;
    filterSelect.addEventListener("change", () => {
      courseApprovalFilter = filterSelect.value;
      renderMappingTable(u);
    });

    renderMappingTable(u);
  }

  function approvalBadge(status) {
    if (status === "yes") return `<span class="badge approved">Pre-approved</span>`;
    if (status === "no") return `<span class="badge not-approved">Not approved</span>`;
    return `<span class="badge unspecified">Unspecified</span>`;
  }

  function courseListHtml(courses) {
    return courses
      .map(
        (c) => `<div class="course-cell">
          <div class="code">${escapeHtml(c.code)}</div>
          ${c.title ? `<div class="title">${escapeHtml(c.title)}</div>` : ""}
          ${c.units != null ? `<div class="units">${c.units} units</div>` : ""}
        </div>`
      )
      .join("");
  }

  function renderMappingTable(u) {
    const wrap = document.getElementById("mappingTableWrap");
    let rows = u.courses;
    if (courseApprovalFilter) rows = rows.filter((c) => c.approved === courseApprovalFilter);

    if (rows.length === 0) {
      wrap.innerHTML = `<p class="link-note">No mappings match this filter.</p>`;
      return;
    }

    wrap.innerHTML = `
      <table class="mapping-table">
        <thead>
          <tr>
            <th>Partner university course</th>
            <th>NUS course</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (c) => `
            <tr>
              <td>${courseListHtml(c.puCourses)}</td>
              <td>${courseListHtml(c.nusCourses)}</td>
              <td class="approval-cell">${approvalBadge(c.approved)}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    `;
  }

  // ---------- events ----------
  function selectUniversity(name) {
    selectedUniName = name;
    courseApprovalFilter = "";
    render();
    renderDetail(findUni(name));
  }

  function bindEvents() {
    [el.search, el.courseSearch].forEach((input) => input.addEventListener("input", render));
    [el.regionFilter, el.countryFilter, el.approvalFilter, el.sortBy].forEach((s) =>
      s.addEventListener("change", render)
    );
    el.shortlistOnly.addEventListener("change", () => {
      activeTab = el.shortlistOnly.checked ? "shortlist" : "all";
      syncTabButtons();
      render();
    });

    el.tabs.forEach((btn) => {
      btn.addEventListener("click", () => {
        activeTab = btn.dataset.tab;
        el.shortlistOnly.checked = activeTab === "shortlist";
        syncTabButtons();
        render();
      });
    });

    el.resetFilters.addEventListener("click", () => {
      el.search.value = "";
      el.courseSearch.value = "";
      el.regionFilter.value = "";
      el.countryFilter.value = "";
      el.approvalFilter.value = "";
      el.sortBy.value = "name";
      el.shortlistOnly.checked = false;
      activeTab = "all";
      syncTabButtons();
      render();
    });

    el.universityList.addEventListener("click", (e) => {
      const starBtn = e.target.closest("[data-star]");
      if (starBtn) {
        e.stopPropagation();
        toggleShortlist(starBtn.dataset.star);
        return;
      }
      const row = e.target.closest(".uni-row");
      if (row) selectUniversity(row.dataset.name);
    });
  }

  function syncTabButtons() {
    el.tabs.forEach((btn) => btn.classList.toggle("active", btn.dataset.tab === activeTab));
  }

  // ---------- init ----------
  fetch("data/data.json")
    .then((r) => r.json())
    .then((data) => {
      DATA = data;
      populateFilterOptions();
      bindEvents();
      render();
    })
    .catch((err) => {
      el.universityList.innerHTML = `<li class="empty-msg">Failed to load data.json — ${escapeHtml(err.message)}. Make sure you're viewing this via a local server, not file://.</li>`;
    });
})();
