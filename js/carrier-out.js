/* BoringRate — outbound carrier links, single source.
 *
 * Every carrier link in the rate tools (auto /, /home/, /renters/) is built here.
 * The tool passes the carrier's canonical site; this returns the href to use.
 *
 *  - Non-partner carriers: canonical URL + UTM tags, so the carrier's own analytics
 *    credit BoringRate for the visit (the links are rel=noreferrer, so without UTMs
 *    these clicks land as "direct").
 *  - Partner carriers (affiliate / pay-per-quote programs): the program's tracking
 *    URL with sub-IDs, rel="sponsored".
 *
 * RULE: partnership changes the link only. It never changes rank order, the rate
 * estimate, or filing coverage. Do not read PARTNERS anywhere in ranking code.
 *
 * Adding a partner = one entry below. Sub-ID placeholders:
 *   {product} auto|home|renters   {state} 2-letter code or ""   {source} rank|compare
 * Example (Impact):
 *   "Root Insurance": { network: "impact",
 *     url: "https://root.sjv.io/c/XXXX/YYYY/ZZZZ?subId1={product}&subId2={state}&subId3={source}",
 *     products: ["auto"] },
 */
(function () {
  var PARTNERS = {
  };

  var UTM = "utm_source=boringrate&utm_medium=referral&utm_campaign=";

  function fill(tpl, ctx) {
    return tpl.replace(/\{(product|state|source)\}/g, function (_, k) {
      return encodeURIComponent((ctx && ctx[k]) || "");
    });
  }

  function withUtm(url, product) {
    if (!url || url === "#") return url;
    return url + (url.indexOf("?") > -1 ? "&" : "?") + UTM + encodeURIComponent(product || "");
  }

  // Returns { href, rel, partner }. ctx = { product, state, source }.
  window.brCarrierOut = function (name, canonicalUrl, ctx) {
    var p = PARTNERS[name];
    if (p && p.url && (!p.products || p.products.indexOf(ctx && ctx.product) > -1)) {
      return { href: fill(p.url, ctx), rel: "sponsored noopener", partner: true };
    }
    return { href: withUtm(canonicalUrl, ctx && ctx.product), rel: "noopener noreferrer", partner: false };
  };

  // Shown under the results only when a partner link is actually on screen.
  window.BR_PARTNER_NOTE =
    '<div class="rank-partner-note">Ranked by estimated price, never by payment. ' +
    'Some carrier links pay us a referral fee when you get a quote; that never moves a carrier up the list or changes a number. ' +
    '<a href="/editorial-standards.html#independence">How we stay independent &rarr;</a></div>';

  try {
    var st = document.createElement("style");
    st.textContent = ".rank-partner-note{margin-top:10px;padding-top:10px;border-top:1px dotted var(--rule,#ccc);color:var(--ink-mute,#666);}";
    document.head.appendChild(st);
  } catch (e) {}
})();
