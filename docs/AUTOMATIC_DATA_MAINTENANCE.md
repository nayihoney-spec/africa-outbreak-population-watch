# Automatic data maintenance contract

Site: https://africa-outbreak-population-watch.nayihoney.chatgpt.site
Repository: https://github.com/nayihoney-spec/africa-outbreak-population-watch
Canonical dataset: data/published.json on main. Do not use the Sites bundled fallback as the current writer base.

## Live path

GitHub Actions `Validate and refresh public-health data` runs every six hours at :17 UTC, and when its collector/tests change. It fetches CDC and ECDC directly, parses only the DRC confirmed-count block, keeps report dates distinct from data-through dates, and compares counts. No homepage-total or multinational total substitution. These publishers may share upstream figures; matching is not independent epidemiological confirmation.

It rejects missing fields, dates in the future, source reports over 14 days old, unequal source counts, date regression, decreasing cumulative values, and jumps over 50%. Failed comparisons retain the complete prior published.json; maintenance.json records the failed check and Actions fails visibly. A legitimate corrected count needs documented source review before overriding a decrease gate. Historical missing years remain missing, and multi-year outbreaks are never split into invented annual figures.

Successful runs validate latest/event mapping and publish one complete JSON bundle in one Git commit. The three legacy JSON files are derived copies. Browser pages load the same canonical bundle from raw.githubusercontent.com with cache busting and no-store, validate it, and otherwise load the bundled last-good fallback. A page reload retrieves updates without republishing Sites. An already open page keeps its coherent snapshot until reload. A data badge shows revision, data-through date, check time, source links and fallback/stale state. Staleness uses the last successful validation time, not an invented new epidemiological date.

## Cloud maintenance audit (every six hours)

1. Read the repository's latest main revision, this contract, published.json, maintenance.json, and relevant Actions runs. Retrieve official-source pages with current tools; do not assume the last conversation's data is current.
2. Re-run or independently reproduce CDC/ECDC parsing, source-date and DRC scope comparison. Read newer WHO, DRC health authority and ReliefWeb reports for conflicts; ReliefWeb reposts are not independent sources. Retain last-good numbers on conflicting time/geography/definition. Record unresolved conflicts and notify the owner; do not silently merge counts.
3. For all configured national travel-authority URLs in published.json, inspect destination-specific official wording and effective date. Preserve regional applicability and original language. Never interpret an HTTP 200 response as verification of an alert level. Update a level only with destination-specific evidence, official URL, verified_at, source_published_at (null if unavailable), checked, validation exactly "verified", and a short evidence excerpt or content hash. Current UI hides numerical/wording levels after 48 hours without renewed verification. Generic ministry homepages are registry-only, not validated DRC alerts. If not validated, set validation="pending", retain the link, and do not invent a level. Persist all verified alert changes atomically in published.json; do not update advisories.json alone.
4. Review official WHO/CDC treatment, research and history changes; propose uncertain changes as pending. Population/displacement statistics remain unimplemented until a versioned official dataset and definition can be verified. Never invent visitors or demographic estimates.
5. Before a write, refresh GitHub blob SHA; preserve unrelated fields. Validate schema_version=1, IDs unique, nonnegative integer counts, deaths <= cases, latest/current event equality, as-of dates, valid HTTPS official URLs, no HTML markup, two matching official current-count evidence records. When changing advisories only, preserve the outbreak verification.checked_at; set published_at and a new revision and advisories.updated_at. Do not claim a data date became newer merely because checked_at changed.
6. Write canonical data/published.json through GitHub connector with its current SHA, or run the tested collector and commit its validated outputs. Read the file back from GitHub at the returned commit and compare exact semantic JSON and revision. Also GET the public raw URL with cache busting, verify it equals the new canonical object, and confirm the live Site still contains the data-client loader and permits raw.githubusercontent.com in CSP. Retry cache propagation briefly; report any inability to verify. No need to republish Sites for routine data writes.
7. Report only meaningful updates or blockers to the owner, with evidence links. A saved schedule is not evidence that a future run succeeded. Persist audit time/outcome in data/maintenance.json, preserving the last successful collector result if reporting a separate audit.

## Verification and rollback

Run `python -m unittest discover -s tests -p 'test_*.py'`, `python scripts/update_data.py`, JS syntax checks, and build with `python scripts/build_static.py`. The collector uses only Python stdlib. To recover, restore a previously validated canonical bundle by a new commit; do not rewrite history. Keep original source timestamps.

## Limits

Counts can be delayed when official sources publish at different times; disagreement intentionally blocks automatic promotion. GitHub Actions schedules can be delayed by GitHub. Raw data connectivity can fail; fallback remains dated. Browser interaction QA was unavailable in the deployment environment; parser, failure gates, live HTTP data and asset checks are performed separately. No guarantee that upstream official data itself is error-free.

## Primary reporting date and terminology

The public current-outbreak as_of is CDC report_as_of, matching the primary current-situation page. ECDC retains its own report_as_of and data_through in verification.sources; do not relabel those as CDC dates. Current cards use DRC confirmed cases and confirmed deaths only. Historical counts follow CDC reported-event totals, with source links and case-basis notes. Site-derived cumulative sums, cumulative shares and ratios must always be labeled calculated; they are not official annual incidence. Virus species labels follow CDC taxonomy: Orthoebolavirus zairense and Orthoebolavirus bundibugyoense.
