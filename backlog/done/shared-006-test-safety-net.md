# Test safety net for every route in every app

### Who

- Developers (and the owner, who relies on tests instead of reading code)

### What

- Yamb, Sjoelen and Home have no tests at all. Squash has route smoke tests and POST-flow tests, but its stats pages are only rendered with almost no data.
- Before adding login protection (shared-004a) or refactoring views (shared-001), we need proof that every page still works.

### Why

- Catches regressions automatically in CI instead of the owner finding them by clicking around.
- Gives shared-004a one place that lists every write URL, so a single test can prove anonymous users can't write anywhere.

### Acceptance Criteria

- [x] Every named route in `home`, `yamb`, `sjoelen` and `squash` has a GET test that returns 200 (or the expected redirect), **with realistic data present**, so leaderboards, statistics, H2H and dashboards actually compute something.
- [x] Squash: the existing smoke tests are kept; add data-filled GETs for leaderboard, H2H and statistics, including the `set_type` and `include_incomplete` toggles.
- [x] Every create, edit and delete flow in every app has a POST happy-path test that checks the database changed as expected.
- [x] Besides "the page loads", add **data-rule tests** for each app's model logic (for example squash set completeness, yamb scoresheet totals, sjoelen score calculation), with edge cases such as ties and boundary scores. For squash, these are the tests from [`squash-003`](squash-003-incomplete-set-detection.md), including the 22-22 set. That bug proves a page can load fine while the data is wrong.
- [x] Admin save flows for the models people correct by hand (at least squash matches with sets) have a test showing the saved values are exactly what was entered.
- [x] A project-wide test lists every write URL across all apps (squash included) and fails if a new URL pattern appears that isn't classified as "read" or "write". That way new write views can't slip through unnoticed.
- [x] The full suite passes in CI.

### Notes

- Test data comes from small factory or helper functions per app, not fixtures copied from production.
- Wedding already has its own tests and its own auth. Include its URLs in the read/write classification, but its auth stays as it is.
- Done 2026-11-28. The write-URL registry is in `yamb_scores/config/url_registry.py`. Three bugs it found are marked as expected failures until they're fixed: squash-003, squash-004 and sjoelen-002.
