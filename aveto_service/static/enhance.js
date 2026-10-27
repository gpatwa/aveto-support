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
  var ready = document.getElementById("ready");
  var suggestHint = document.getElementById("sugg-hint");
  var busy = false;
  var band = "ok";
  var ticker = null;
  var moved = false;
  var TOP_GAP = 16; // px between the viewport top and the result heading

  var WAITING = [
    ["Looking through the docs", "Your question has been sent."],
    ["Still working", "This is taking longer than usual. Please keep this page open."],
    ["Still waiting", "This is taking more than a minute. You can keep waiting. If nothing changes, reload the page and ask again."]
  ];

  if (!q.disabled) {
    hint.textContent = "Up to 500 characters. Press Ctrl+Enter or Cmd+Enter to send.";
  }
  if (suggestHint) {
    suggestHint.textContent = "Choose one to put it in the box, then press Ask. Three are answered in the docs and one is not, so you can see both outcomes.";
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (text !== undefined) { e.textContent = text; }
    return e;
  }
  function chars(s) { return Array.from(s).length; }

  function clear() {
    live.textContent = "";
    extra.textContent = "";
    region.removeAttribute("aria-labelledby");
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
    region.setAttribute("aria-labelledby", "result-title");
    return { box: s, heading: h };
  }
  function stopTicker() {
    if (ticker) { clearInterval(ticker); ticker = null; }
  }
  function resultFirst() { // the order the server gives a result page; runs at most once
    if (moved || region.compareDocumentPosition(form) & Node.DOCUMENT_POSITION_FOLLOWING) { return; }
    var main = form.parentNode;
    var n = main.querySelector("h1").nextElementSibling.nextElementSibling;
    var take = [];
    while (n && n !== form) { take.push(n); n = n.nextElementSibling; }
    take.forEach(function (e) { main.appendChild(e); });
    moved = true;
  }
  function land() {
    resultFirst();
    region.focus({ preventScroll: true });
    var t = document.getElementById("result-title") || region;
    window.scrollTo(0, Math.max(0, t.getBoundingClientRect().top + window.pageYOffset - TOP_GAP));
  }
  function settle(field) {
    busy = false;
    stopTicker();
    button.removeAttribute("aria-disabled");
    button.textContent = "Ask";
    if (field) {
      q.focus();
    } else {
      land();
    }
  }
  function showNetworkError() {
    var r = box("error", "We couldn't reach the service", true);
    r.box.appendChild(el("p", "", "Check your connection and try again. Your question is still in the box."));
    settle(false);
  }
  function showWaiting() {
    var r = box("note", WAITING[0][0], false);
    var body = el("p", "", WAITING[0][1]);
    var clock = el("p", "elapsed", "Waiting: 0 seconds");
    clock.setAttribute("aria-hidden", "true");
    r.box.appendChild(body);
    r.box.appendChild(clock);
    var started = Date.now();
    var stage = 0;
    ticker = setInterval(function () {
      var s = Math.floor((Date.now() - started) / 1000);
      clock.textContent = "Waiting: " + s + (s === 1 ? " second" : " seconds");
      var next = s >= 60 ? 2 : (s >= 8 ? 1 : 0);
      if (next !== stage) {
        stage = next;
        r.heading.textContent = WAITING[next][0];
        body.textContent = WAITING[next][1];
      }
    }, 1000);
  }
  function revealCopy() {
    if (!navigator.clipboard || !navigator.clipboard.writeText) { return; }
    Array.prototype.forEach.call(document.querySelectorAll("button.copy"), function (b) { b.hidden = false; });
  }
  function fieldError(msg) {
    qerr.textContent = msg;
    q.setAttribute("aria-invalid", "true");
  }
  function clearFieldError() {
    qerr.textContent = "";
    q.removeAttribute("aria-invalid");
  }
  function adopt(from, to) {
    if (!from) { return; }
    Array.prototype.forEach.call(from.childNodes, function (n) { to.appendChild(document.importNode(n, true)); });
  }
  // The server renders every result card; the page only swaps in what it sent.
  function swap(doc) {
    var parsed = doc.getElementById("result");
    if (!parsed) { showNetworkError(); return; }
    clear();
    adopt(doc.getElementById("result-live"), live);
    adopt(doc.getElementById("result-extra"), extra);
    var label = parsed.getAttribute("aria-labelledby");
    if (label) { region.setAttribute("aria-labelledby", label); }
    var pe = doc.getElementById("q-error");
    var msg = pe ? pe.textContent : "";
    if (msg) { fieldError(msg); } else { clearFieldError(); }
    revealCopy();
    settle(msg !== "");
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
    var n = chars(q.value.trim());
    if (n === 0) { fieldError("Enter a question before you press Ask."); q.focus(); return; }
    if (n > LIMIT) { fieldError("Shorten your question to 500 characters or fewer."); q.focus(); return; }
    busy = true;
    button.setAttribute("aria-disabled", "true");
    button.textContent = "Asking...";
    showWaiting();
    fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ question: q.value }),
      credentials: "omit",
      cache: "no-store",
      referrerPolicy: "no-referrer",
      redirect: "follow"
    }).then(function (res) {
      return res.text();
    }).then(function (html) {
      swap(new DOMParser().parseFromString(html, "text/html"));
    }).catch(function () {
      showNetworkError();
    });
  });

  // A suggestion loads into the box and does not send; without this script it asks straight away.
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f || !f.classList || !f.classList.contains("suggest")) { return; }
    e.preventDefault();
    q.value = f.elements.question.value;
    clearFieldError();
    update();
    status.textContent = "Question loaded. Press Ask to send it.";
    q.focus();
  });

  document.addEventListener("click", function (e) {
    var t = e.target && e.target.closest ? e.target : null;
    if (!t) { return; }
    var docs = t.closest("a[data-count]");
    if (docs && navigator.sendBeacon) {
      navigator.sendBeacon("/count/docs-click");
      return;
    }
    var copy = t.closest("button.copy");
    if (!copy) { return; }
    var chip = copy.parentNode.querySelector("a.chip");
    var label = copy.firstChild;
    navigator.clipboard.writeText(chip.href).then(function () {
      label.nodeValue = "Copied";
      status.textContent = "Link copied.";
      setTimeout(function () { label.nodeValue = "Copy link"; }, 2000);
    }, function () {
      status.textContent = "Couldn't copy the link. Use the source link instead.";
    });
  });

  revealCopy();
  update();
  if (location.hash === "#result" && document.getElementById("result-title")) { land(); }

  if (ready && !button.disabled) {
    fetch("/warm", { method: "POST", credentials: "omit", cache: "no-store", referrerPolicy: "no-referrer" })
      .then(function (res) { return res.json(); })
      .then(function (d) { if (d && d.ready === true) { ready.textContent = "Ready to search the docs."; } })
      .catch(function () {});
  }
})();
