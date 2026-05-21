# BoringRate — Notes to Revisit

## SEO: Organization Schema — sameAs
`index.html` has Organization schema but `sameAs` is currently an empty array.
When BoringRate gets any of these, add the URL to `sameAs`:
- Twitter/X profile
- LinkedIn page
- Crunchbase entry
- Any other authoritative directory listing

This links the site to a known entity in Google's Knowledge Graph.

---

## SEO: Homepage FAQ Section
Adding a visible 3–4 question FAQ block to the bottom of `index.html` would
unlock FAQPage schema on the homepage (Google requires the Q&A to exist as
visible HTML — schema alone isn't enough).

Candidate questions:
- "How does BoringRate rank carriers?"
- "Is BoringRate free?"
- "How accurate are the rates?"
- "Does BoringRate sell my information?"

This is a **design decision** — it changes the homepage layout. Revisit when
ready to discuss what the FAQ section would look like.

---

## SEO: BreadcrumbList Schema
Article pages don't have BreadcrumbList schema. Adding it would help Google
display the site hierarchy in SERP (e.g. "BoringRate > Carriers > GEICO").
Lower priority than FAQPage/Organization — lower ranking impact, mostly a
display enhancement. Would need to be batched across all 250 pages.

---

## Content: Miami + Tucson Agent Pools
`mia` (Miami) and `tuc` (Tucson) metro agent pools still only have 3 agents.
All other pools have 4+. Need 1 confirmed local independent agency for each:
- **Miami**: needs a true Miami-local independent (not a broker/aggregator)
- **Tucson**: currently has Greene/Coriano/State48, which are Phoenix-focused AZ
  agencies — need a Tucson-specific replacement or addition

---

## SEO: Internal Linking Audit
No systematic review of internal links has been done. Potential gaps:
- State pages → relevant metro pages within that state
- Carrier pages → relevant compare pages (e.g. GEICO page → GEICO vs X pages)
- Guide articles → coverage.html calculator (some already link, not all)
- Coverage.html → coverage-guide.html (and vice versa)
