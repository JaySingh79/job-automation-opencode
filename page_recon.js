// One-shot page recon for a form/apply page.
//
// Goal (per the "get everything at once" rule): on landing, make ONE call that
// returns every interactive element fused across the layers a browser agent can
// read — DOM, accepted input, accessibility semantics, CSS visibility/geometry —
// keyed in top-to-bottom page order. After this call the only remaining work is
// DECIDE values -> FILL. No per-field snapshots, no re-finding refs.
//
// How to run: paste the body of `reconFn` into mcp__playwright__browser_evaluate.
// It returns JSON (stringify-safe). Pair it in the SAME turn with:
//   - browser_snapshot                (accessibility tree + @refs to act on)
//   - browser_take_screenshot fullPage (then image_slicing.js -> keyed slices)
//   - read_console_messages / read_network_requests (only if debugging)
// so DOM+a11y+CSS+visual+console all arrive together.
//
// Element `key` here == DOM order index. It aligns with the slice keys from
// image_slicing.js by the element's `rect.y` (which slice a field sits in).

function reconFn() {
  const vis = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      shown: s.display !== "none" && s.visibility !== "hidden" && +s.opacity !== 0 && r.width > 0 && r.height > 0,
      rect: { x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height) },
    };
  };
  const nameOf = (el) => {
    const lb = el.getAttribute("aria-label");
    if (lb) return lb.trim();
    const by = el.getAttribute("aria-labelledby");
    if (by) { const n = by.split(/\s+/).map((id) => (document.getElementById(id) || {}).textContent || "").join(" ").trim(); if (n) return n; }
    if (el.id) { const l = document.querySelector(`label[for="${el.id}"]`); if (l) return l.textContent.trim(); }
    const wrap = el.closest("label"); if (wrap) return wrap.textContent.trim();
    return el.name || el.getAttribute("placeholder") || "";
  };

  const sel = "input,select,textarea,button,[role=radio],[role=checkbox],[role=combobox],[role=button],[role=switch],a[href],[contenteditable=true]";
  const els = Array.from(document.querySelectorAll("main " + sel + ", form " + sel));
  const uniq = Array.from(new Set(els)); // main/form overlap

  const items = uniq.map((el, i) => {
    const v = vis(el);
    const tag = el.tagName.toLowerCase();
    const o = {
      key: i,                                   // page-order key
      tag,
      type: el.type || el.getAttribute("type") || null,
      role: el.getAttribute("role") || null,
      name: nameOf(el).replace(/\s+/g, " ").slice(0, 80),
      value: (el.value !== undefined ? el.value : (el.textContent || "")).toString().slice(0, 60),
      // accepted-input contract (what the field will actually take)
      accepts: {
        required: el.getAttribute("aria-required") === "true" || el.required || null,
        maxlength: el.getAttribute("maxlength") || null,
        pattern: el.getAttribute("pattern") || null,
        inputmode: el.getAttribute("inputmode") || null,
        min: el.getAttribute("min") || null,
        max: el.getAttribute("max") || null,
      },
      // a11y state
      checked: el.getAttribute("aria-checked") || (el.checked ? "true" : null),
      pressed: el.getAttribute("aria-pressed") || null,
      expanded: el.getAttribute("aria-expanded") || null,
      disabled: el.disabled || el.getAttribute("aria-disabled") === "true" || null,
      invalid: el.getAttribute("aria-invalid") === "true" || null,
      // css/layout
      shown: v.shown,
      rect: v.rect,
      // honeypot guard — never fill these
      honeypot: /honeypot/i.test(el.name || "") || /honeypot/i.test(nameOf(el)) || getComputedStyle(el).display === "none",
    };
    if (tag === "select") o.options = Array.from(el.options).map((op) => op.textContent.trim()).slice(0, 40);
    return o;
  })
  // drop pure-decoration/hidden noise, keep real controls (and honeypots, flagged)
  .filter((o) => o.name || o.type || o.role || o.tag !== "a");

  return JSON.stringify({
    url: location.href,
    title: document.title,
    scrollHeight: document.documentElement.scrollHeight,
    counts: { total: items.length, required: items.filter((x) => x.accepts.required).length,
              empty_required: items.filter((x) => x.accepts.required && !x.value).length,
              honeypots: items.filter((x) => x.honeypot).length },
    fields: items,
  });
}

module.exports = { reconFn };
