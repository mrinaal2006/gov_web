const STRINGS = {
  en: {
    nav_file: "Report a problem", nav_track: "Track a complaint", nav_privacy: "Privacy", switch_lang: "বাংলা",
    operated_by: "Operated by", contact: "Contact",
    browser_tip: "Use any browser on your computer for a better experience.",
    rights: "All rights reserved.",
    emergency: "For emergencies, call 112. Do not use this form.",
    skip: "Skip to main content", nav_how: "How it works", nav_topics: "What you can report",
    eyebrow: "Citizen complaint service",
    home_title: "Report a local problem. Track the response.",
    home_lead: "Tell us about water, power, roads, health and other local problems in the language you use every day, then follow what happens next.",
    home_file: "Report a problem", home_track: "Track a complaint",
    quick_title: "Already reported a problem?", quick_hint: "Enter your tracking ID to see the latest update.",
    how_kicker: "How it works", how_title: "Three simple steps from problem to response",
    step1: "Describe the problem", step1_d: "Write it in your own words and choose your village. It takes a few minutes.",
    step2: "Get a tracking ID", step2_d: "Keep this ID safe. It is the only way to check your complaint.",
    step3: "Read the response", step3_d: "Officers review your complaint, update its status and reply on the tracking page.",
    topics_kicker: "What you can report", topics_title: "Everyday problems in your village, from water to school meals",
    t_water: "Water", t_water_d: "No supply, dirty water or a broken tubewell",
    t_power: "Electricity", t_power_d: "Power cuts and burnt transformers",
    t_roads: "Roads", t_roads_d: "Broken roads and blocked routes",
    t_health: "Health", t_health_d: "Health centre and doctor availability",
    t_ration: "Ration", t_ration_d: "Ration shop and food supply problems",
    t_pension: "Pension", t_pension_d: "Old age pension not received",
    t_clean: "Sanitation", t_clean_d: "Blocked drains and dirty water on roads",
    t_school: "Education", t_school_d: "School and mid-day meal problems",
    why_kicker: "Why use it", why_title: "Built around the people who report problems",
    v1: "Your language", v1_d: "Write in Bengali, English or Banglish. There is no special format to learn.",
    v2: "A clear record", v2_d: "Your tracking ID shows your complaint's status and every response in one place.",
    v3: "Your privacy", v3_d: "Your name and mobile number are optional and only signed-in officers can see them.",
    closing_title: "Seen a problem in your area?", closing_d: "Report it now and keep track of the response.",
    foot_about: "A complaint service for local problems, in Bengali, English and Banglish.",
    foot_citizens: "For citizens", foot_service: "About this service", foot_officer: "Officer sign-in",
    file_title: "Report a problem", text_label: "What is the problem?",
    text_hint: "Say what happened, where, and for how long. Do not include Aadhaar or bank details.",
    village_label: "Village", village_none: "My village is not listed",
    name_label: "Your name (optional)", phone_label: "Mobile number (optional)", phone_hint: "Only officers can see it, in case they need to call you.",
    consent: "I agree that my complaint and contact details can be used to handle this complaint, as described in the privacy notice.",
    submit: "Send complaint", sending: "Sending...",
    done_title: "Complaint received", done_keep: "Save this tracking ID. You need it to check for a response.",
    suggested: "Suggested department", place: "Village", target: "Response target", not_found: "To be confirmed",
    done_note: "The department was suggested automatically. An officer can change it.",
    done_track: "Track this complaint", done_another: "Report another problem",
    track_title: "Track a complaint", id_label: "Tracking ID", track_btn: "Check status", your_complaint: "Your complaint",
    department: "Department", received: "Received", overdue: "Past response target", history: "Updates",
    s_received: "Received", s_in_progress: "In progress", s_resolved: "Resolved", s_rejected: "Closed without action",
    privacy_title: "Privacy notice",
    p1h: "What we collect", p1: "Your complaint, your village, and your name and mobile number if you choose to give them.",
    p2h: "How it is used", p2: "To send your complaint to the right department, find patterns in complaints from an area, and let officers respond to you. Software suggests the department and an urgency score, and officers can review them. To suggest the score, your complaint text is sent to Google's Gemini AI service, with phone and Aadhaar numbers hidden. Your name and mobile number fields are not sent.",
    p3h: "Who can see it", p3: "Signed-in officers can see everything. Anyone with your tracking ID can see the complaint text, status and responses, but not your name or number. Keep your ID private.",
    p4h: "Masking", p4: "Phone and Aadhaar numbers written in the complaint text are hidden automatically. Other details you write, such as names, are not, so please leave them out.",
    p5h: "Questions or removal", p5: "To ask about your data or request its correction or removal, contact the operator named below.",
    err: "Something went wrong. Please try again.",
  },
  bn: {
    nav_file: "সমস্যা জানান", nav_track: "অভিযোগের অবস্থা দেখুন", nav_privacy: "গোপনীয়তা", switch_lang: "English",
    operated_by: "পরিচালনায়", contact: "যোগাযোগ",
    browser_tip: "আরও ভালো অভিজ্ঞতার জন্য আপনার কম্পিউটারের যেকোনো ব্রাউজার ব্যবহার করুন।",
    rights: "সর্বস্বত্ব সংরক্ষিত।",
    emergency: "জরুরি অবস্থায় ১১২ নম্বরে ফোন করুন। এই ফর্ম ব্যবহার করবেন না।",
    skip: "মূল অংশে যান", nav_how: "কীভাবে কাজ করে", nav_topics: "কী জানাতে পারেন",
    eyebrow: "নাগরিক অভিযোগ পরিষেবা",
    home_title: "এলাকার সমস্যা জানান। উত্তরের খোঁজ রাখুন।",
    home_lead: "জল, বিদ্যুৎ, রাস্তা, স্বাস্থ্য ও এলাকার অন্যান্য সমস্যা নিজের ভাষায় জানান, তারপর কী হচ্ছে তার খোঁজ রাখুন।",
    home_file: "সমস্যা জানান", home_track: "অভিযোগের অবস্থা দেখুন",
    quick_title: "আগেই সমস্যা জানিয়েছেন?", quick_hint: "সর্বশেষ আপডেট দেখতে ট্র্যাকিং আইডি লিখুন।",
    how_kicker: "কীভাবে কাজ করে", how_title: "সমস্যা থেকে উত্তর পর্যন্ত তিনটি সহজ ধাপ",
    step1: "সমস্যাটি লিখুন", step1_d: "নিজের ভাষায় লিখুন এবং আপনার গ্রাম বেছে নিন। কয়েক মিনিটই যথেষ্ট।",
    step2: "ট্র্যাকিং আইডি নিন", step2_d: "এই আইডি যত্নে রাখুন। অভিযোগের খোঁজ নেওয়ার এটিই একমাত্র উপায়।",
    step3: "উত্তর পড়ুন", step3_d: "আধিকারিকরা অভিযোগ দেখে অবস্থা জানাবেন এবং ট্র্যাকিং পাতায় উত্তর দেবেন।",
    topics_kicker: "কী জানাতে পারেন", topics_title: "আপনার গ্রামের দৈনন্দিন সমস্যা, জল থেকে মিড ডে মিল পর্যন্ত",
    t_water: "জল", t_water_d: "জল নেই, নোংরা জল বা নষ্ট টিউবওয়েল",
    t_power: "বিদ্যুৎ", t_power_d: "বিদ্যুৎ বিভ্রাট ও পুড়ে যাওয়া ট্রান্সফর্মার",
    t_roads: "রাস্তা", t_roads_d: "ভাঙা রাস্তা ও বন্ধ পথ",
    t_health: "স্বাস্থ্য", t_health_d: "স্বাস্থ্যকেন্দ্র ও ডাক্তারের অনুপস্থিতি",
    t_ration: "রেশন", t_ration_d: "রেশন দোকান ও খাদ্য সরবরাহের সমস্যা",
    t_pension: "পেনশন", t_pension_d: "বার্ধক্য ভাতা না পাওয়া",
    t_clean: "পরিচ্ছন্নতা", t_clean_d: "বন্ধ ড্রেন ও রাস্তায় নোংরা জল",
    t_school: "শিক্ষা", t_school_d: "স্কুল ও মিড ডে মিলের সমস্যা",
    why_kicker: "কেন ব্যবহার করবেন", why_title: "যাঁরা সমস্যা জানান, তাঁদের কথা ভেবে তৈরি",
    v1: "আপনার ভাষা", v1_d: "বাংলা, ইংরেজি বা বাংলিশে লিখুন। কোনো বিশেষ নিয়ম শেখার দরকার নেই।",
    v2: "স্পষ্ট রেকর্ড", v2_d: "ট্র্যাকিং আইডিতে অভিযোগের অবস্থা ও সব উত্তর এক জায়গায় দেখা যায়।",
    v3: "আপনার গোপনীয়তা", v3_d: "নাম ও মোবাইল নম্বর দেওয়া ঐচ্ছিক, এবং শুধু সাইন-ইন করা আধিকারিকরা তা দেখতে পান।",
    closing_title: "এলাকায় কোনো সমস্যা দেখেছেন?", closing_d: "এখনই জানান এবং উত্তরের খোঁজ রাখুন।",
    foot_about: "এলাকার সমস্যার জন্য অভিযোগ পরিষেবা, বাংলা, ইংরেজি ও বাংলিশে।",
    foot_citizens: "নাগরিকদের জন্য", foot_service: "এই পরিষেবা সম্পর্কে", foot_officer: "আধিকারিক সাইন-ইন",
    file_title: "সমস্যা জানান", text_label: "সমস্যাটি কী?",
    text_hint: "কী হয়েছে, কোথায় এবং কত দিন ধরে তা লিখুন। আধার বা ব্যাঙ্কের তথ্য লিখবেন না।",
    village_label: "গ্রাম", village_none: "আমার গ্রাম তালিকায় নেই",
    name_label: "আপনার নাম (ঐচ্ছিক)", phone_label: "মোবাইল নম্বর (ঐচ্ছিক)", phone_hint: "প্রয়োজনে ফোন করার জন্য শুধু আধিকারিকরা এটি দেখতে পাবেন।",
    consent: "গোপনীয়তা বিজ্ঞপ্তি অনুযায়ী আমার অভিযোগ ও যোগাযোগের তথ্য এই অভিযোগের কাজে ব্যবহার করতে আমি সম্মত।",
    submit: "অভিযোগ পাঠান", sending: "পাঠানো হচ্ছে...",
    done_title: "অভিযোগ পাওয়া গেছে", done_keep: "এই ট্র্যাকিং আইডি রেখে দিন। উত্তর দেখতে এটি লাগবে।",
    suggested: "প্রস্তাবিত বিভাগ", place: "গ্রাম", target: "উত্তরের লক্ষ্য", not_found: "নিশ্চিত করা হবে",
    done_note: "বিভাগটি স্বয়ংক্রিয়ভাবে প্রস্তাব করা হয়েছে। আধিকারিক এটি বদলাতে পারেন।",
    done_track: "এই অভিযোগের খোঁজ নিন", done_another: "আরেকটি সমস্যা জানান",
    track_title: "অভিযোগের অবস্থা দেখুন", id_label: "ট্র্যাকিং আইডি", track_btn: "অবস্থা দেখুন", your_complaint: "আপনার অভিযোগ",
    department: "বিভাগ", received: "পাওয়া গেছে", overdue: "উত্তরের সময়সীমা পেরিয়ে গেছে", history: "আপডেট",
    s_received: "পাওয়া গেছে", s_in_progress: "কাজ চলছে", s_resolved: "সমাধান হয়েছে", s_rejected: "ব্যবস্থা ছাড়াই বন্ধ",
    privacy_title: "গোপনীয়তা বিজ্ঞপ্তি",
    p1h: "আমরা কী সংগ্রহ করি", p1: "আপনার অভিযোগ, গ্রাম, এবং আপনি দিতে চাইলে নাম ও মোবাইল নম্বর।",
    p2h: "কীভাবে ব্যবহার হয়", p2: "অভিযোগ সঠিক বিভাগে পাঠাতে, এলাকার অভিযোগের ধরন বুঝতে এবং আধিকারিকদের উত্তর দিতে। সফটওয়্যার বিভাগ ও জরুরিতার স্কোর প্রস্তাব করে, আধিকারিকরা তা যাচাই করতে পারেন। স্কোর প্রস্তাবের জন্য আপনার অভিযোগের লেখা গুগলের জেমিনি এআই পরিষেবায় পাঠানো হয়, ফোন ও আধার নম্বর আড়াল করে। আপনার নাম ও মোবাইল নম্বরের ঘর পাঠানো হয় না।",
    p3h: "কে দেখতে পায়", p3: "সাইন-ইন করা আধিকারিকরা সব দেখতে পান। আপনার ট্র্যাকিং আইডি যার কাছে আছে সে অভিযোগ, অবস্থা ও উত্তর দেখতে পাবে, কিন্তু নাম বা নম্বর নয়। আইডি গোপন রাখুন।",
    p4h: "তথ্য আড়াল করা", p4: "অভিযোগে লেখা ফোন ও আধার নম্বর স্বয়ংক্রিয়ভাবে আড়াল হয়। নামের মতো অন্য তথ্য আড়াল হয় না, তাই সেগুলি লিখবেন না।",
    p5h: "প্রশ্ন বা মুছে ফেলা", p5: "আপনার তথ্য নিয়ে প্রশ্ন, সংশোধন বা মুছে ফেলার জন্য নীচে উল্লেখিত পরিচালকের সঙ্গে যোগাযোগ করুন।",
    err: "কিছু ভুল হয়েছে। আবার চেষ্টা করুন।",
  },
};

const DEPARTMENTS_BN = { Water: "জল", Electricity: "বিদ্যুৎ", Roads: "রাস্তা", Health: "স্বাস্থ্য", Ration: "রেশন", Pension: "পেনশন", Sanitation: "পরিচ্ছন্নতা", Education: "শিক্ষা" };

let lang = "en";
try { lang = localStorage.getItem("lang") === "bn" ? "bn" : "en"; } catch (e) { /* private window */ }
const t = (key) => STRINGS[lang][key] || STRINGS.en[key] || key;
const dept = (name) => (lang === "bn" && DEPARTMENTS_BN[name]) || name;
const $ = (selector) => document.querySelector(selector);

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value);
  }
  node.append(...children);
  return node;
}

function when(value, dateOnly) {
  if (!value) return "";
  const options = dateOnly ? { dateStyle: "medium" } : { dateStyle: "medium", timeStyle: "short" };
  return new Date(value).toLocaleString(lang === "bn" ? "bn-IN" : "en-IN", { ...options, timeZone: "Asia/Kolkata" });
}

async function api(path, options = {}) {
  const init = { credentials: "same-origin", ...options };
  if (options.body) {
    init.method = options.method || "POST";
    init.headers = { "Content-Type": "application/json" };
    init.body = JSON.stringify(options.body);
  }
  const response = await fetch(path, init);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail) ? t("err") : data.detail;
    throw Object.assign(new Error(detail || t("err")), { status: response.status });
  }
  return data;
}

function translate() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-t]").forEach((node) => { node.textContent = t(node.dataset.t); });
}

let siteConfig = null;
async function loadConfig() {
  siteConfig = await api("/api/config");
  document.querySelectorAll("[data-service]").forEach((node) => { node.textContent = siteConfig.service_name; });
  renderChrome();
  return siteConfig;
}

function renderCopyright() {
  const name = siteConfig ? siteConfig.service_name : "Samasya Radar";
  document.querySelectorAll("[data-copyright]").forEach((node) => {
    node.textContent = `© ${new Date().getFullYear()} ${name}. ${t("rights")}`;
  });
}

function renderChrome() {
  renderCopyright();
  if (!siteConfig) return;
  const foot = $("#operator");
  if (foot) {
    foot.textContent = siteConfig.live
      ? `${t("operated_by")}: ${siteConfig.operator}${siteConfig.contact ? ` · ${t("contact")}: ${siteConfig.contact}` : ""}`
      : t("browser_tip");
  }
}

const onLanguageChange = [];
function setupLanguage() {
  const button = $("#lang");
  if (button) {
    button.addEventListener("click", () => {
      lang = lang === "en" ? "bn" : "en";
      try { localStorage.setItem("lang", lang); } catch (e) { /* private window */ }
      translate();
      renderChrome();
      onLanguageChange.forEach((fn) => fn());
    });
  }
  translate();
  renderCopyright();
}

function setupHomePage() {
  loadConfig();
  $("#quick").addEventListener("submit", (event) => {
    event.preventDefault();
    location.href = `/track.html?id=${encodeURIComponent($("#quick-id").value.trim())}`;
  });
}

function statusBadge(status) {
  return el("span", { class: `status ${status}`, text: t(`s_${status}`) });
}

function setupFilePage() {
  const form = $("#complaint");
  const select = $("#village");
  const fill = () => {
    const chosen = select.value;
    select.replaceChildren(el("option", { value: "", text: t("village_none") }));
    [...siteConfig.villages].sort((a, b) => a.village.localeCompare(b.village)).forEach((v) => {
      select.append(el("option", { value: v.village, text: `${lang === "bn" ? v.village_bn : v.village} (${v.block})` }));
    });
    select.value = chosen;
  };
  loadConfig().then(fill);
  onLanguageChange.push(fill);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#error");
    const button = $("#send");
    error.hidden = true;
    button.disabled = true;
    button.textContent = t("sending");
    try {
      const data = new FormData(form);
      const result = await api("/api/complaints", { body: {
        text: data.get("text"), village: data.get("village") || null, contact_name: data.get("name") || null,
        contact_phone: data.get("phone") || null, consent: data.get("consent") === "on", website: data.get("website") || null,
      } });
      $("#ticket").textContent = result.id;
      $("#r-dept").textContent = dept(result.department);
      $("#r-place").textContent = result.village || t("not_found");
      $("#r-due").textContent = when(result.due_at, true);
      $("#r-track").href = `/track.html?id=${encodeURIComponent(result.id)}`;
      form.reset();
      $("#form-panel").hidden = true;
      $("#done-panel").hidden = false;
      window.scrollTo(0, 0);
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
    button.disabled = false;
    button.textContent = t("submit");
  });
}

function setupTrackPage() {
  loadConfig();
  const form = $("#lookup");
  const out = $("#result");
  let last = null;
  const draw = () => {
    if (!last) return;
    const c = last;
    const list = el("ol", { class: "timeline" });
    c.timeline.forEach((e) => {
      list.append(el("li", {},
        el("time", { text: when(e.created_at) }),
        e.status ? statusBadge(e.status) : "",
        e.public_message ? el("div", { class: "quote", text: e.public_message }) : ""));
    });
    out.replaceChildren(
      el("div", { class: "head" }, el("h2", { text: c.id }), statusBadge(c.status)),
      c.overdue ? el("div", { class: "error", text: t("overdue") }) : "",
      el("div", { class: "facts" },
        el("div", {}, el("small", { text: t("department") }), el("b", { text: dept(c.department) })),
        el("div", {}, el("small", { text: t("place") }), el("b", { text: c.village || t("not_found") })),
        el("div", {}, el("small", { text: t("received") }), el("b", { text: when(c.received_at, true) })),
        el("div", {}, el("small", { text: t("target") }), el("b", { text: when(c.due_at, true) }))),
      el("h3", { text: t("your_complaint") }), el("div", { class: "quote", text: c.text }),
      el("h3", { text: t("history"), style: "margin-top:20px" }), list);
    out.hidden = false;
  };
  onLanguageChange.push(draw);
  const look = async (id) => {
    const error = $("#error");
    error.hidden = true;
    out.hidden = true;
    last = null;
    try {
      last = await api(`/api/complaints/${encodeURIComponent(id.trim())}`);
      draw();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  };
  form.addEventListener("submit", (event) => { event.preventDefault(); look($("#tid").value); });
  const given = new URLSearchParams(location.search).get("id");
  if (given) { $("#tid").value = given; look(given); }
}

function setReveal(button, visible) {
  document.getElementById(button.dataset.reveal).type = visible ? "text" : "password";
  button.textContent = visible ? "Hide" : "Show";
  button.setAttribute("aria-pressed", visible);
  button.setAttribute("aria-label", visible ? "Hide password" : "Show password");
}

function hidePasswords() {
  document.querySelectorAll("[data-reveal]").forEach((button) => setReveal(button, false));
}

function setupActivatePage() {
  loadConfig();
  const given = new URLSearchParams(location.search).get("email");
  if (given) $("#a-email").value = given;
  $("#activate").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#error");
    error.hidden = true;
    try {
      await api("/api/officer/activate", { body: {
        email: $("#a-email").value, code: $("#a-code").value, password: $("#a-password").value } });
      $("#a-password").value = "";
      hidePasswords();
      $("#form-panel").hidden = true;
      $("#done-panel").hidden = false;
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  });
}

function setupResetPage() {
  loadConfig();
  const showCodeForm = (email, note) => {
    $("#r-email").value = email;
    $("#r-note").textContent = note;
    $("#ask-panel").hidden = true;
    $("#code-panel").hidden = false;
  };
  const given = new URLSearchParams(location.search).get("email");
  if (given) showCodeForm(given, "Enter the code from your email and choose a new password.");
  $("#forgot").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#f-error");
    const button = $("#f-send");
    error.hidden = true;
    button.disabled = true;
    try {
      const email = $("#f-email").value.trim();
      const result = await api("/api/officer/forgot", { body: { email } });
      showCodeForm(email, result.dev_code
        ? `Email is not set up on this computer, so nothing was sent. Code for testing: ${result.dev_code}`
        : `${result.message} Check your spam folder too. The code works for 30 minutes.`);
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
    button.disabled = false;
  });
  $("#r-again").addEventListener("click", () => {
    $("#f-email").value = $("#r-email").value;
    $("#r-error").hidden = true;
    $("#code-panel").hidden = true;
    $("#ask-panel").hidden = false;
  });
  $("#reset").addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = $("#r-error");
    error.hidden = true;
    try {
      await api("/api/officer/reset", { body: {
        email: $("#r-email").value, code: $("#r-code").value, password: $("#r-password").value } });
      $("#r-password").value = "";
      hidePasswords();
      $("#code-panel").hidden = true;
      $("#done-panel").hidden = false;
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupLanguage();
  document.querySelectorAll("[data-reveal]").forEach((button) => button.addEventListener("click", () => {
    setReveal(button, document.getElementById(button.dataset.reveal).type === "password");
  }));
  const page = document.body.dataset.page;
  if (page === "home") setupHomePage();
  else if (page === "file") setupFilePage();
  else if (page === "activate") setupActivatePage();
  else if (page === "reset") setupResetPage();
  else if (page === "track") setupTrackPage();
  else if (page !== "officer") loadConfig();
});
