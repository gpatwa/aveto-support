(function () {
  "use strict";
  var LIMIT = 500;
  var form = document.getElementById("ask-form");
  if (!form || !window.fetch) { return; }
  var q = document.getElementById("q");
  var count = document.getElementById("q-count");
  var qerr = document.getElementById("q-error");
  var status = document.getElementById("q-status");
  var hint = document.getElementById("q-hint");
  var button = document.getElementById("ask-button");
  var region = document.getElementById("result");
  var live = document.getElementById("result-live");
  var extra = document.getElementById("result-extra");
  var issueUrl = document.getElementById("link-issue").href;
  var docsUrl = document.getElementById("link-docs").href;
  var busy = false;
  var band = "ok";
  var longTimer = null;

  hint.textContent = "Up to 500 characters. Press Ctrl+Enter or Cmd+Enter to send.";

  var STATES = {
    no_confident_match: ["note", "The docs don't answer this", "No confident match was found, so nothing is shown. You can change your question and ask again, or open a GitHub issue.", false, "issue"],
    judge_error: ["error", "We couldn't decide this time", "Something went wrong while checking the passages, so none are shown. Please try again.", true, ""],
    rate_limited: ["error", "Question limit reached", "You can ask 10 questions an hour. Please try again later. Your question is still in the box.", true, ""],
    paused: ["note", "Paused for today", "Ask the Docs has a daily limit and today's has been used. This is not a fault. You can read the docs on GitHub or open an issue.", false, "both"],
    service_off: ["note", "The service is off", "Ask the Docs is switched off right now. You can read the docs on GitHub or open an issue.", true, "both"],
    empty: ["error", "Please enter a question", "Type a question about Aveto, then press Ask. Nothing was sent.", true, ""],
    network: ["error", "We couldn't reach the service", "Check your connection and try again. Your question is still in the box.", true, ""]
  };

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (text !== undefined) { e.textContent = text; }
    return e;
  }
  function link(href, text) {
    var a = el("a", "", text);
    a.href = href;
    a.rel = "noopener noreferrer";
    return a;
  }
  function chars(s) { return Array.from(s).length; }
  function lines(a, b) { return a === b ? "Line " + a : "Lines " + a + " to " + b; }
  function lowerLines(a, b) { return a === b ? "line " + a : "lines " + a + " to " + b; }

  function clear() {
    live.textContent = "";
    extra.textContent = "";
  }
  function box(kind, title, alert) {
    clear();
    var s = el("div", "state state-" + kind);
    var icon = el("span", "icon", kind === "error" ? "!" : "");
    icon.setAttribute("aria-hidden", "true");
    var h = el("h2", "", title);
    h.id = "result-title";
    if (alert) { h.setAttribute("role", "alert"); }
    s.appendChild(icon);
    s.appendChild(h);
    live.appendChild(s);
    return { box: s, heading: h };
  }
  function showState(key, field) {
    var d = STATES[key];
    var r = box(d[0], d[1], d[3]);
    r.box.appendChild(el("p", "", d[2]));
    var p = el("p", "links");
    if (d[4] === "issue" || d[4] === "both") { p.appendChild(link(issueUrl, "Open a GitHub issue")); }
    if (d[4] === "both") { p.appendChild(link(docsUrl, "Read the docs on GitHub")); }
    if (p.firstChild) { r.box.appendChild(p); }
    settle(field);
  }
  function showTooLong(n) {
    var r = box("error", "Your question is too long", true);
    r.box.appendChild(el("p", "", "Questions can be up to " + LIMIT + " characters. Yours is " + n + ". Shorten it and ask again. Nothing was sent."));
    settle(true);
  }
  function showAnswer(data) {
    var items = [];
    data.files.forEach(function (f) {
      f.passages.forEach(function (p) { items.push([f.path, p]); });
    });
    var n = items.length;
    var r = box("answer", "The docs answer this", false);
    r.heading.appendChild(el("span", "found", n === 1 ? "Found 1 passage." : "Found " + n + " passages."));
    var ol = el("ol", "passages");
    items.forEach(function (it, i) {
      var path = it[0], p = it[1];
      var span = lowerLines(p.line_start, p.line_end);
      var li = el("li");
      var art = el("article");
      art.setAttribute("aria-labelledby", "p" + (i + 1) + "-title");
      var h3 = el("h3");
      h3.id = "p" + (i + 1) + "-title";
      h3.appendChild(el("code", "", path));
      art.appendChild(h3);
      art.appendChild(el("p", "meta", "Section: " + p.heading + ". " + lines(p.line_start, p.line_end)));
      var lp = el("p");
      lp.appendChild(link(p.url, "View " + span + " of " + path + " on GitHub"));
      art.appendChild(lp);
      var pre = el("pre", "passage");
      pre.tabIndex = 0;
      pre.setAttribute("role", "region");
      pre.setAttribute("aria-label", "Passage text from " + path + ", " + span);
      pre.appendChild(el("code", "", p.text));
      art.appendChild(pre);
      li.appendChild(art);
      ol.appendChild(li);
    });
    extra.appendChild(ol);
    settle(false);
  }
  function showWaiting(long) {
    var r = box("note", long ? "Still working" : "Looking through the docs", false);
    r.box.appendChild(el("p", "", long ? "The service may be waking up. This can take up to a minute. Please keep this page open." : "This usually takes a few seconds."));
    var d = el("span", "dots");
    d.setAttribute("aria-hidden", "true");
    var dot = el("span", "dot");
    dot.setAttribute("aria-hidden", "true");
    r.heading.appendChild(d);
    r.heading.appendChild(dot);
  }
  function settle(field) {
    busy = false;
    button.removeAttribute("aria-disabled");
    button.textContent = "Ask";
    if (longTimer) { clearTimeout(longTimer); longTimer = null; }
    if (field) {
      q.focus();
    } else {
      region.focus();
    }
  }
  function fieldError(msg) {
    qerr.textContent = msg;
    q.setAttribute("aria-invalid", "true");
  }
  function clearFieldError() {
    qerr.textContent = "";
    q.removeAttribute("aria-invalid");
  }

  function update() {
    var n = chars(q.value);
    var over = n > LIMIT;
    count.textContent = over ? (n - LIMIT) + " characters over the limit of " + LIMIT + ". Shorten your question." : n + " of " + LIMIT + " characters";
    count.className = over ? "error" : "";
    var next = over ? "over" : (n >= 450 ? "near" : "ok");
    if (next !== band) {
      if (next === "over") { status.textContent = "Over the limit by " + (n - LIMIT) + " characters"; }
      else if (next === "near") { status.textContent = (LIMIT - n) + " characters left"; }
      else { status.textContent = ""; }
      band = next;
    }
  }
  q.addEventListener("input", function () { clearFieldError(); update(); });
  q.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (busy) { return; }
    var text = q.value;
    var n = chars(text.trim());
    if (n === 0) { fieldError("Please enter a question."); showState("empty", true); return; }
    if (n > LIMIT) {
      fieldError("Your question is too long.");
      showTooLong(n);
      return;
    }
    busy = true;
    button.setAttribute("aria-disabled", "true");
    button.textContent = "Asking...";
    showWaiting(false);
    longTimer = setTimeout(function () { showWaiting(true); }, 8000);
    fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text }),
      credentials: "omit",
      cache: "no-store",
      referrerPolicy: "no-referrer"
    }).then(function (res) {
      return res.json();
    }).then(function (data) {
      var o = data.outcome;
      if (o === "answer") { showAnswer(data); }
      else if (o === "too_long") { fieldError("Your question is too long."); showTooLong(data.length); }
      else if (o === "empty_question" || o === "unusable_question" || o === "bad_request") { fieldError("Please enter a question."); showState("empty", true); }
      else if (o === "body_too_large") { fieldError("Your question is too long."); showTooLong(chars(text)); }
      else if (STATES[o]) { showState(o, false); }
      else { showState("judge_error", false); }
    }).catch(function () {
      showState("network", false);
    });
  });
  update();
})();
