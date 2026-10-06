# Slice 2 Execution Temp: Squash Full Views Refactor

Status: Active
Owner: Product Manager + Planning workflow
Created: 2026-07-23
Delete/Archive Rule: Remove this file after Slice 2 is completed, verified, and released.

## Scope

- Split squash views into dedicated modules while preserving behavior.
- Keep URLs and route names unchanged.
- Use `views/__init__.py` re-exports for compatibility.

Target modules:
- `views/matches.py`
- `views/players.py`
- `views/leaderboard.py`
- `views/h2h.py`
- `views/statistics.py`
- `views/__init__.py`

## Phase Plan

| Phase | Files | Acceptance checks | Risks |
|---|---|---|---|
| 0. Baseline guardrails | tests + squash route smoke checks | Existing squash tests pass; mandatory route smoke checks pass for all squash endpoints; baseline POST flow checks pass for new match, new session, and player create/edit/delete | Hidden regressions later |
| 1. Package cutover (no behavior changes) | `views/*` + `views/__init__.py` | `urls.py` unchanged; explicit URL resolution checks pass for every squash route; explicit import compatibility checks pass; baseline tests unchanged and green | Import breakage from file-to-package conversion |
| 2A. Matches split | `views/matches.py` | new_match/new_session/match_list behavior and redirects unchanged; Phase 0/1 smoke checks still green | POST flow behavior drift |
| 2B. Players split | `views/players.py` | player list/create/edit/delete behavior and redirects unchanged; Phase 0/1 smoke checks still green | CRUD drift |
| 3. Leaderboard hardening | `views/leaderboard.py`, stats service tests | existing sorting behavior and query-count guard remain green; invalid sort fallback tests pass | Sorting regression |
| 4. H2H split + minimal extraction | `views/h2h.py`, optional service helper | h2h sorting/filtering deterministic with tests; set_type filtering parity checks pass | Aggregation correctness and query cost |
| 5. Statistics split + safe helper extraction | `views/statistics.py`, pure helpers only | fixed context contract test passes; default + set_type + include_incomplete toggles pass | Large logic surface and edge-case drift |
| 6. Final verification | all touched files | full squash suite green; reviewer and verification gates passed; rollback drill dry run recorded | Residual uncovered edge cases |

## Service Extraction Map

Move now:
- Keep leaderboard service in `squash/services/stats.py` and only add small pure helpers as needed.
- Extract H2H aggregation helper (pure function) if it reduces view complexity without changing behavior.
- Extract pure statistics transformers (box-data shaping, extremes ranking helper).

Move later:
- Query optimization/annotation redesign for h2h/statistics.
- Shared utilities across apps only after repeated stable duplication is proven.

## Commit Boundaries

1. Baseline tests + missing route smoke tests.
2. File-to-package cutover + `views/__init__.py` re-exports (no logic changes).
3. Matches module split only (Phase 2A).
4. Players module split only (Phase 2B).
5. Leaderboard module split + fallback/sort tests.
6. H2H module split + targeted tests.
7. Statistics module split + context-contract tests.
8. Cleanup + full verification gates.

## Test Plan by Phase

- Phase 0:
	- run existing squash test suite
	- add and run route smoke checks for all squash URLs: index, new_match, new_session, match_list, leaderboard, h2h, statistics, player list/create/edit/delete
	- add and run baseline POST checks for new_match, new_session, player create/edit/delete redirect behavior
- Phase 1:
	- rerun all Phase 0 checks unchanged
	- add URL resolution checks using `reverse()` + `resolve()` for every squash route name
	- add import compatibility check that `from squash import views` still exposes all URL-referenced callables
- Phase 2A:
	- run match/session flow tests and route smoke regression checks
- Phase 2B:
	- run player CRUD tests and route smoke regression checks
- Phase 3:
	- run leaderboard sorting/filter tests + query-count guard + invalid sort fallback checks
- Phase 4:
	- run h2h player selection/sort/set_type filter tests
- Phase 5:
	- run statistics default + set_type + include_incomplete tests
	- run fixed context contract test expecting keys:
		- `total_matches`, `total_sets`, `incomplete_sets`, `unique_players_count`, `sets_11_point`, `sets_21_point`, `set_type_filter`, `include_incomplete`, `player_performance_data`, `player_stats`, `player_box_data`, `player_box_data_11`, `player_box_data_21`, `matches_by_date`, `match_extremes`
- Phase 6:
	- run full squash test suite + manual smoke pass
	- execute rollback dry run checklist on local branch

## Rollback Runbook (Required)

Pre-cutover requirement:
1. Create pre-cutover tag before Phase 1 merge candidate (example: `slice2-pre-cutover`).

Rollback trigger conditions:
1. Any route/import break.
2. Any failed critical smoke check post-merge candidate.
3. Any high-severity reviewer or verification finding opened after merge candidate.

Rollback steps:
1. Revert last phase commit first (`git revert <commit_sha>`).
2. If issue persists, revert to pre-cutover tag baseline (`git revert <range>` or reset/redeploy using the tagged revision in release process).
3. Redeploy reverted revision through normal release flow.

Post-rollback validation:
1. Re-run mandatory squash route smoke checks.
2. Re-run squash test suite subset for touched areas.
3. Confirm routes and key flows are restored (match/session/player/leaderboard/h2h/statistics).

Rollback evidence to store in this file:
1. Trigger reason.
2. Reverted commit(s).
3. Validation check results.

## Reviewer + Verification Go/No-Go Checklist

Go only if all are true:
- URL patterns and names unchanged.
- `views/__init__.py` re-exports complete for `urls.py` compatibility.
- All phase tests are green.
- No unresolved high-severity reviewer findings.
- Rollback is documented as commit-level revert with no migration concerns.

No-go if any are true:
- Import or route resolution break.
- Template context key drift on statistics.
- Sorting/filter regressions on leaderboard/h2h.
- Missing evidence for required phase checks.

## Estimate (Slice 2)

- Optimistic: 1.5 focused days
- Likely: 2.5 to 3.5 days
- Conservative: 5 days

## Live Execution Log (Update Each Prompt)

Current phase: Phase 1 Architecture and Refactor review
Last completed phase: Phase 0
Open blockers: 0 for the Architecture design review; implementation remains gated
Next required action: Send the Architecture and Refactor Agent prompt recorded below.

## Product Manager + Planning Handoff (2026-10-06)

- Status: GO to Architecture and Refactor review; this is not an implementation approval.
- Intake: Slice 2 remains active. The scope is covered by `shared-001-refactor-python-code.md`; no separate Phase 1 to-do item exists. Other statistics, login/player, and Yamb backlog items are out of scope.
- Evidence: `squash/urls.py` still imports `.views` and refers to 11 view callables. The current implementation is `squash/views.py`, so package conversion must preserve those imports through `views/__init__.py`. The route/POST smoke tests are present, and `manage.py test squash.tests` passed all 11 tests on 2026-10-06.
- Phase 1 acceptance checks: (1) `urls.py` remains unchanged; (2) `reverse()`/`resolve()` checks pass for every named squash route; (3) `from squash import views` exposes every callable referenced by `urls.py`; (4) Phase 0 route smoke and POST redirect checks still pass unchanged; (5) the full existing squash test suite remains green; (6) no behavior changes are introduced.
- Preconditions/findings for Architecture review: none block design review. Before implementation is eligible, add/run the explicit Phase 1 URL-resolution and import-compatibility checks, rerun Phase 0 checks, and create the required pre-cutover tag before the merge candidate. The existing smoke tests check route responses and redirects, not URL resolver mapping or the re-export contract.
- Next target agent: Architecture and Refactor Agent.
- Required inputs: plan, roadmap, this slice log, adopted way of working, umbrella refactor backlog item, current `squash/urls.py`, `squash/views.py`, and route/POST smoke tests.

### Decision Notes

- 2026-07-23: Slice 2 temp execution file created as source of running execution context.
- 2026-07-23: Option B selected (Reviewer challenge pass before implementation).
- 2026-07-23: Product Manager validation complete; GO decision for Phase 0 only.
- 2026-07-23: Phase 0 implemented (route smoke + POST redirect guardrails) and squash suite passed (11 tests); next gate is Reviewer.
- 2026-07-23: Reviewer gate outcome for Phase 0 is GO; planning workflow now requires PM GO/NO-GO on definitive way of working before Phase 1 prompt issuance.
- 2026-07-23: WAY_OF_WORKING rewritten to v2 with a single authoritative chain and explicit Reviewer pre/post implementation gates; next step is Reviewer re-review.
- 2026-07-23: Reviewer re-review returned GO for WAY_OF_WORKING v2 adoption.
- 2026-07-23: PM decision recorded as GO ADOPT for WAY_OF_WORKING v2; governance gate closed.

## Reviewer Challenge Findings (2026-07-23)

Status: Blocked

Findings by severity:
- High: Baseline test coverage is too narrow for file-to-package cutover risk.
- High: Missing explicit URL resolution and import compatibility gate for Phase 1.
- Medium: Phase 2 commit boundary is too broad (matches + players together).
- Medium: Rollback plan lacks operational steps (tag, revert commands, post-revert smoke checks).
- Medium: Statistics context contract is not explicit enough for regression detection.

Required changes before implementation:
1. Add mandatory pre-cutover route smoke checks for all squash endpoints and core POST flows.
2. Add explicit URL resolution/import compatibility acceptance check for Phase 1.
3. Split Phase 2 into two commits: 2A matches, 2B players.
4. Add rollback runbook with pre-cutover tag, revert procedure, and post-revert smoke checks.
5. Add explicit statistics context key contract test with fixed expected key set.

Recommendation:
- Block Phase 1 start until all required changes are applied to this file and acknowledged by Product Manager.

## Planning Remediation Summary (2026-07-23)

Reviewer finding to change mapping:
1. Narrow baseline coverage -> Added mandatory full squash route smoke checks and baseline POST flow checks in Phase 0.
2. Missing URL/import gate -> Added explicit `reverse()`/`resolve()` route checks and import compatibility checks in Phase 1.
3. Phase 2 too broad -> Split into Phase 2A (matches) and Phase 2B (players), with separate commits.
4. Rollback not operational -> Added explicit pre-cutover tag, rollback triggers, step-by-step rollback actions, and post-rollback validation evidence.
5. Statistics context contract weak -> Added fixed expected key contract for statistics context in Phase 5 tests.

## Single Next Prompt To Send

Persistence rule:
- Keep this prompt synchronized with `backlog/plan/ROADMAP.md` in the same turn.
- Chat may repeat the prompt, but chat is never the source of truth.

Copy/paste exactly:

```
You are the Architecture and Refactor Agent.

Read:
- backlog/plan/plan.md
- backlog/plan/ROADMAP.md
- backlog/plan/slices/slice-2-execution-temp.md
- backlog/plan/WAY_OF_WORKING.md
- backlog/to-do/shared-001-refactor-python-code.md
- yamb_scores/squash/urls.py
- yamb_scores/squash/views.py
- yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py

Context:
- WAY_OF_WORKING v2 is adopted (PM GO).
- PM intake and Planning handoff are complete (GO, 2026-10-06).
- Active work is Slice 2 Phase 1: package cutover only, with no behavior changes.
- The current squash test suite passed (11 tests) on 2026-10-06.

Task:
1. Review the Phase 1 package-cutover design without implementing it.
2. Recommend the safe file-to-package mapping and complete views/__init__.py re-export set needed to keep urls.py unchanged.
3. Assess URL/import compatibility risks, test gates, rollback shape, and any remaining preconditions before Reviewer and Challenge review.
4. Keep the scope to package cutover only: no behavior, URL, template, model, or service changes.
5. Return one handoff artifact with: Status, evidence summary, blockers (or None), next target agent, and required inputs.
6. Provide exactly one single next prompt to send, targeting the Reviewer and Challenge Agent. Do not implement code.

Output format:
- Status (GO/BLOCK/N/A)
- Evidence summary
- Blockers
- Next target agent
- Required inputs for next agent
- Single next prompt to send
```