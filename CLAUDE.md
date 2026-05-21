# BoringRate — Claude Notes

## Patch script safety rule

**Never replace an entire `<script>...</script>` block to inject new JS.**

The pattern that caused widespread JS loss (commit history: `patch_hamburger_js.py`):
```python
# DANGEROUS — wipes any co-located JS in the same block
start = html.rfind('<script>', 0, marker_pos)
end = html.find('</script>', marker_pos)
html = html[:start] + new_js + html[end + 9:]
```

Several pages (index.html, coverage.html, state-rankings.html, 66 compare pages, 7 guide articles) had unique JS co-located in the same `<script>` block as the old hamburger nav marker. Replacing the block wiped the calculator, app logic, ZIP bar handlers, Supabase email form, etc. Recovery required extracting from git `41fb75c`.

**Safe pattern instead — insert a new block, don't replace:**
```python
# SAFE — insert new <script> before the existing block
idx = html.find(MARKER)
html = html[:idx] + NEW_SCRIPT_BLOCK + html[idx:]
```

Or if you truly must replace a block, extract and preserve any non-target JS first.
