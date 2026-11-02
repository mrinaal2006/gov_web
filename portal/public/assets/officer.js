let summaryData = null;
let map = null;
let heat = null;
let currentUser = null;
let fitted = false;
let openPane = null;

function show(id, on) { $(id).hidden = !on; }

async function start() {
  await loadConfig();
  [...siteConfig.villages].sort((a, b) => a.village.localeCompare(b.village)).forEach((v) => {
    $("#a-village").append(el("option", { value: v.village, text: `${v.village} (${v.block})` }));
  });
  try {
    currentUser = await api("/api/officer/me");
    enter();
  } catch (err) {
    show("#login-view", true);
  }
}

function enter() {
  show("#login-view", false);
  show("#desk", true);
  $("#who").textContent = `${currentUser.name} (${currentUser.email})`;
  $("#tab-team").hidden = currentUser.role !== "admin";
  openTab("overview");
}

function openTab(name) {
  openPane = name;
  if (name !== "overview" && heat) { // a resize would make it redraw at zero size; drawMap builds it again
    map.removeLayer(heat);
    heat = null;
  }
  document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === name));
  document.querySelectorAll("[data-pane]").forEach((p) => { p.hidden = p.dataset.pane !== name; });
  if (name === "overview") loadSummary();
  if (name === "queue") loadQueue();
  if (name === "team") loadTeam();
}

function periodQuery(choice, from, to) {
  if (choice !== "dates") return new URLSearchParams({ days: choice });
  return new URLSearchParams({ start: from, end: to });
}

async function loadSummary() {
  const choice = $("#days").value;
  if (choice === "dates" && (!$("#o-from").value || !$("#o-to").value)) return; // waiting for both dates
  summaryData = await api(`/api/officer/summary?${periodQuery(choice, $("#o-from").value, $("#o-to").value)}`);
  const s = summaryData.totals;
  const metric = (label, value, bad) => el("div", { class: `metric${bad && value ? " bad" : ""}` }, el("small", { text: label }), el("b", { text: String(value) }));
  $("#metrics").replaceChildren(
    metric("Complaints", s.complaints), metric("Pending", s.pending), metric("Past response target", s.overdue, true),
    metric("High urgency score (70+), pending", s.high_urgency), metric("Needs review", s.needs_review));

  const hot = $("#hotspots");
  hot.replaceChildren();
  if (!summaryData.hotspots.length) hot.append(el("div", { class: "calm", text: "No hotspots in the last 48 hours" }));
  summaryData.hotspots.forEach((h) => hot.append(el("div", { class: "hot",
    text: `${h.department} in ${h.village} (${h.block}): ${h.complaints} complaints in 48 hours. Latest ${when(h.latest)}` })));

  const filter = $("#q-dept");
  if (filter.options.length <= 1) summaryData.departments.forEach((d) => filter.append(el("option", { value: d, text: d })));

  drawMap();
  const newest = await api("/api/officer/complaints?view=all&sort=newest&limit=5");
  $("#latest").replaceChildren(...newest.map((c) => el("tr", { class: "pick", tabindex: "0", onclick: () => openComplaint(c.id),
    onkeydown: (e) => { if (e.key === "Enter") openComplaint(c.id); } },
    el("td", { text: when(c.received_at) }), el("td", { class: "clip", text: c.text }), el("td", { text: c.department }),
    el("td", { text: c.village || "Unknown" }), el("td", {}, statusBadge(c.status)))));
  if (!newest.length) $("#latest").append(el("tr", {}, el("td", { colspan: "5", text: "No complaints yet." })));
  const body = $("#card");
  body.replaceChildren();
  if (!summaryData.scorecard.length) body.append(el("tr", {}, el("td", { colspan: "6", text: "No complaints in this period." })));
  summaryData.scorecard.forEach((r) => body.append(el("tr", {},
    el("td", { text: r.block }), el("td", { text: r.department }), el("td", { class: "num", text: r.complaints }),
    el("td", { class: "num", text: r.pending }), el("td", { class: "num", text: r.overdue }),
    el("td", { class: "num", text: r.avg_days === null ? "-" : r.avg_days }))));
}

function drawMap() {
  if (openPane !== "overview") return; // the heat layer cannot draw on a hidden map
  const points = summaryData.points.map((p) => [p.lat, p.lon, Math.max(p.urgency, 5) / 100]);
  if (!map) {
    map = L.map("map").setView([23.95, 87.7], 9);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 16, attribution: "&copy; OpenStreetMap contributors",
      referrerPolicy: "strict-origin-when-cross-origin", // OpenStreetMap blocks image requests that hide the site
    }).addTo(map);
  }
  map.invalidateSize({ pan: false }); // the map keeps its old size while its tab was hidden
  if (heat) map.removeLayer(heat);
  // Scale to the data so that only the busiest places reach red
  const peak = Math.max(1, points.reduce((sum, p) => sum + p[2], 0) / 60);
  heat = L.heatLayer(points, { radius: 26, blur: 20, maxZoom: 12, max: peak }).addTo(map);
  if (points.length && !fitted) {
    map.fitBounds(points.map((p) => [p[0], p[1]]), { padding: [24, 24], maxZoom: 11 });
    fitted = true;
  }
}

async function loadQueue() {
  const params = new URLSearchParams({ view: $("#q-view").value, sort: $("#q-sort").value });
  if ($("#q-dept").value) params.set("department", $("#q-dept").value);
  const rows = await api(`/api/officer/complaints?${params}`);
  const body = $("#queue");
  body.replaceChildren();
  const now = new Date().toISOString();
  rows.forEach((c) => {
    const late = ["received", "in_progress"].includes(c.status) && c.due_at < now;
    body.append(el("tr", { class: "pick", tabindex: "0", onclick: () => openComplaint(c.id),
      onkeydown: (e) => { if (e.key === "Enter") openComplaint(c.id); } },
      el("td", { class: "num", text: c.urgency }),
      el("td", { class: "clip", text: c.text }),
      el("td", { text: c.department }),
      el("td", { text: c.village || "Unknown" }),
      el("td", {}, statusBadge(c.status), late ? el("span", { class: "status overdue", text: "Late" }) : "",
        c.needs_review ? el("span", { class: "status overdue", text: "Review" }) : ""),
      el("td", { text: when(c.received_at, true) })));
  });
  show("#queue-empty", rows.length === 0);
}

async function openComplaint(id) {
  const c = await api(`/api/officer/complaints/${encodeURIComponent(id)}`);
  const box = $("#detail");
  const status = el("select", { id: "u-status" });
  [["received", "Received"], ["in_progress", "In progress"], ["resolved", "Resolved"], ["rejected", "Closed without action"]]
    .forEach(([v, label]) => status.append(el("option", { value: v, text: label })));
  status.value = c.status;
  const department = el("select", { id: "u-dept" });
  summaryData.departments.forEach((d) => department.append(el("option", { value: d, text: d })));
  department.value = c.department;
  const message = el("textarea", { id: "u-message", style: "min-height:90px" });
  const note = el("textarea", { id: "u-note", style: "min-height:60px" });
  const error = el("div", { class: "error", hidden: "" });
  const history = el("ol", { class: "timeline" });
  const scoreReason = c.events.find((e) => e.kind === "urgency");
  c.events.filter((e) => e.kind !== "urgency").forEach((e) => history.append(el("li", {},
    el("time", { text: `${when(e.created_at)}${e.officer_email ? ` · ${e.officer_email}` : ""}` }),
    el("div", { text: e.kind === "status" ? `Status: ${e.status}` : e.kind }),
    e.public_message ? el("div", { class: "quote", text: `Citizen sees: ${e.public_message}` }) : "",
    e.internal_note ? el("div", { class: "quote", text: `Internal: ${e.internal_note}` }) : "")));
  const save = async (event) => {
    event.preventDefault();
    error.hidden = true;
    try {
      await api(`/api/officer/complaints/${encodeURIComponent(id)}`, { body: {
        status: status.value, department: department.value, public_message: message.value, internal_note: note.value } });
      box.close();
      loadQueue();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  };
  box.replaceChildren(
    el("div", { class: "head" }, el("h2", { text: c.id }),
      el("button", { class: "btn alt small", type: "button", text: "Close", onclick: () => box.close() })),
    el("div", { class: "quote", text: c.text }),
    scoreReason ? el("p", { class: "note", text: `Gemini's reason for the score: ${scoreReason.internal_note}` }) : "",
    el("div", { class: "facts" },
      el("div", {}, el("small", { text: "Village" }), el("b", { text: c.village ? `${c.village}, ${c.block}` : "Unknown" })),
      el("div", {}, el("small", { text: "Urgency score (rough guide)" }), el("b", { text: c.urgency })),
      el("div", {}, el("small", { text: "Department confidence" }), el("b", { text: `${Math.round(c.department_confidence * 100)}%` })),
      el("div", {}, el("small", { text: "Response target" }), el("b", { text: when(c.due_at, true) })),
      el("div", {}, el("small", { text: "Name" }), el("b", { text: c.contact_name || "Not given" })),
      el("div", {}, el("small", { text: "Mobile" }), el("b", { text: c.contact_phone || "Not given" }))),
    el("form", { onsubmit: save },
      el("label", { for: "u-status", text: "Status" }), status,
      el("label", { for: "u-dept", text: "Department" }), department,
      el("label", { for: "u-message" }, "Response to the citizen", el("span", { class: "hint", text: "Shown on the tracking page. Required when closing a complaint." })), message,
      el("label", { for: "u-note" }, "Internal note", el("span", { class: "hint", text: "Officers only." })), note,
      error,
      el("button", { class: "btn", style: "margin-top:16px", text: "Save" })),
    el("h3", { text: "History", style: "margin-top:24px" }), history);
  box.showModal();
}

async function loadTeam() {
  const rows = await api("/api/officer/officers");
  const body = $("#team");
  body.replaceChildren();
  rows.forEach((o) => body.append(el("tr", {}, el("td", { text: o.name }), el("td", { text: o.email }), el("td", { text: o.role }),
    el("td", {}, o.email === currentUser.email ? "You"
      : el("button", { class: "btn alt small", type: "button", text: "Remove", "aria-label": `Remove ${o.name}`, onclick: () => removeOfficer(o) })))));
  loadInvites();
}

function drawAnalysis(r) {
  const percent = (p) => `${Math.round(p * 100)}%`;
  const fact = (label, value) => el("div", {}, el("small", { text: label }), el("b", { text: value }));
  const byGemini = r.urgency_source === "gemini";
  const reasons = el("ul", {},
    byGemini ? el("li", { text: `Gemini's reason: ${r.urgency_reason}` })
      : el("li", { text: r.serious_words.length ? `Serious words found: ${r.serious_words.join(", ")}` : "No words from the serious-word list" }),
    el("li", { text: r.village
      ? `${r.similar_7d} similar ${r.department} complaint${r.similar_7d === 1 ? "" : "s"} from ${r.village} in the last 7 days`
      : "No village recognised, so similar complaints could not be counted. Name a listed village in the text, or choose one above" }),
    byGemini ? "" : el("li", { text: "Text length and the current time of day also affect the score" }));
  $("#a-result").replaceChildren(
    el("div", { class: "head" }, el("h2", { text: "Result" }),
      el("span", { class: `status ${r.high ? "overdue" : ""}`, text: r.high ? "High urgency (70+)" : "Below high urgency" })),
    el("div", { class: "metrics", style: "margin-top:12px" },
      el("div", { class: `metric${r.high ? " bad" : ""}` }, el("small", { text: byGemini ? "Urgency score, from Gemini" : "Urgency score, from the backup model" }), el("b", { id: "a-score", text: `${r.urgency}/100` }))),
    el("div", { class: "facts" },
      fact("Department", `${r.department} (${percent(r.confidence)})`),
      fact("Other possibilities", r.departments.slice(1).map((d) => `${d.name} ${percent(d.probability)}`).join(", ")),
      fact("Village", r.village ? `${r.village}, ${r.block}` : "Not recognised")),
    r.needs_review ? el("p", { class: "alert", style: "margin:14px 0", text: `An officer would need to review a complaint like this: ${r.review_reasons.join(", and ")}.` }) : "",
    el("h3", { text: "What influenced the score", style: "margin-top:16px" }), reasons,
    el("p", { class: "note", text: byGemini
      ? "This score is a suggestion from an AI model and has not yet been tested on real complaints. Use your own judgement."
      : "Gemini was not available, so this is a rough guide from the backup model, trained on simulated complaints. Use your own judgement." }));
  $("#a-result").hidden = false;
}

async function loadInvites() {
  const rows = await api("/api/officer/invites");
  const body = $("#invites");
  body.replaceChildren();
  rows.forEach((i) => body.append(el("tr", {}, el("td", { text: i.name }), el("td", { text: i.email }), el("td", { text: i.role }),
    el("td", { text: i.expired ? "Expired" : `Until ${when(i.expires_at)}` }),
    el("td", {},
      el("button", { class: "btn alt small", type: "button", text: "Send new code", "aria-label": `Send new code to ${i.name}`, onclick: () => invite(i) }), " ",
      el("button", { class: "btn alt small", type: "button", text: "Cancel", "aria-label": `Cancel invitation for ${i.name}`, onclick: () => cancelInvite(i) })))));
  show("#invites-panel", rows.length > 0);
}

async function invite(person) {
  const error = $("#team-error");
  const done = $("#team-done");
  error.hidden = true;
  done.hidden = true;
  const result = await api("/api/officer/officers", { body: { name: person.name, email: person.email, role: person.role } });
  done.textContent = result.sent
    ? `Verification code sent to ${result.email}. They can finish at /activate.html.`
    : `Email is not set up on this computer, so nothing was sent. Code for testing ${result.email}: ${result.dev_code}`;
  done.hidden = false;
  loadInvites();
}

async function cancelInvite(person) {
  if (!window.confirm(`Cancel the invitation for ${person.email}? Their code will stop working.`)) return;
  await api(`/api/officer/invites/${encodeURIComponent(person.email)}`, { method: "DELETE" });
  loadInvites();
}

async function removeOfficer(person) {
  if (!window.confirm(`Remove ${person.name} (${person.email})? They will lose access immediately. Their past actions stay in complaint history.`)) return;
  const error = $("#remove-error");
  error.hidden = true;
  try {
    await api(`/api/officer/officers/${encodeURIComponent(person.email)}`, { method: "DELETE" });
    loadTeam();
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  start();
  $("#login").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#login-error");
    error.hidden = true;
    try {
      await api("/api/officer/login", { body: { email: $("#email").value, password: $("#password").value } });
      $("#password").value = "";
      hidePasswords();
      currentUser = await api("/api/officer/me");
      enter();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  });
  $("#logout").addEventListener("click", async () => {
    await api("/api/officer/logout", { method: "POST" });
    location.reload();
  });
  document.querySelectorAll(".tabs button").forEach((b) => b.addEventListener("click", () => openTab(b.dataset.tab)));
  $("#r-period").addEventListener("change", () => {
    const custom = $("#r-period").value === "custom";
    const dates = $("#r-period").value === "dates";
    $("#r-custom-box").hidden = !custom;
    $("#r-custom").required = custom;
    $("#r-dates-box").hidden = !dates;
    $("#r-from").required = dates;
    $("#r-to").required = dates;
  });
  $("#report").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#r-error");
    const done = $("#r-done");
    const button = $("#r-download");
    const period = $("#r-period").value;
    const query = periodQuery(period === "custom" ? $("#r-custom").value : period, $("#r-from").value, $("#r-to").value);
    error.hidden = true;
    done.hidden = true;
    button.disabled = true;
    button.textContent = "Preparing...";
    try {
      const response = await fetch(`/api/officer/report.pdf?${query}`, { credentials: "same-origin" });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(typeof data.detail === "string" ? data.detail : "Please choose a whole number of days from 1 to 365.");
      }
      const url = URL.createObjectURL(await response.blob());
      const name = /filename="([^"]+)"/.exec(response.headers.get("Content-Disposition") || "");
      const link = el("a", { href: url, download: name ? name[1] : "samasya-radar-report.pdf" });
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      done.textContent = "Your report has been downloaded.";
      done.hidden = false;
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
    button.disabled = false;
    button.textContent = "Download PDF";
  });
  $("#analyze").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#a-error");
    const button = $("#a-run");
    error.hidden = true;
    button.disabled = true;
    try {
      drawAnalysis(await api("/api/officer/analyze", { body: { text: $("#a-text").value, village: $("#a-village").value || null } }));
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
    button.disabled = false;
  });
  $("#change-password").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#c-error");
    const done = $("#c-done");
    error.hidden = true;
    done.hidden = true;
    try {
      await api("/api/officer/password", { body: { current_password: $("#c-current").value, new_password: $("#c-new").value } });
      event.target.reset();
      hidePasswords();
      done.textContent = "Your password has been changed. Any other sign-ins have been ended.";
      done.hidden = false;
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  });
  const today = new Date(Date.now() + 5.5 * 3600000).toISOString().slice(0, 10); // India date
  ["#o-from", "#o-to", "#r-from", "#r-to"].forEach((id) => { $(id).max = today; });
  const refreshPeriod = async () => {
    const error = $("#o-error");
    error.hidden = true;
    document.querySelectorAll("[data-range]").forEach((box) => { box.hidden = $("#days").value !== "dates"; });
    try {
      await loadSummary();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  };
  ["#days", "#o-from", "#o-to"].forEach((id) => $(id).addEventListener("change", refreshPeriod));
  $("#q-view").addEventListener("change", loadQueue);
  $("#q-dept").addEventListener("change", loadQueue);
  $("#q-sort").addEventListener("change", loadQueue);
  // New complaints appear by themselves, unless an officer is busy with one
  setInterval(() => {
    if (document.hidden || $("#detail").open || $("#desk").hidden) return;
    if (openPane === "overview") loadSummary().catch(() => {});
    if (openPane === "queue") loadQueue().catch(() => {});
  }, 30000);
  $("#add-officer").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = new FormData(form);
    const error = $("#team-error");
    try {
      await invite({ name: data.get("name"), email: data.get("email"), role: data.get("role") });
      form.reset();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  });
});
