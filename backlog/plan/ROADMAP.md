# Delivery Roadmap: Backend Refactor + Unified Login (Option A)

## How To Use This File

- This file is the session launcher.
- Keep only what is needed to start the next session fast.
- Keep full slice execution details in a temporary per-slice working file under `backlog/plan/slices/`.
- Keep the immediate next prompt (or explicit PM choice) here and mirror it in the active slice temp file.
- Chat summaries are allowed, but chat is never the source-of-truth record for next prompts.

## Current Session State

- Slice 1: Closed
- Active slice: Slice 2 (Squash Full Views Refactor)
- Decision selected: Option B (Reviewer challenge pass before implementation)
- Reviewer status: GO for WAY_OF_WORKING v2 adoption review
- PM decision: GO ADOPT for WAY_OF_WORKING v2
- PM intake: GO (2026-10-06); Slice 2 remains active and is covered by shared-001
- Architecture review: GO to pre-implementation challenge (2026-10-06); design only, not implementation approval
- Reviewer and Challenge: GO to Auth and Domain Model impact assessment (2026-10-15); design handoff only, not implementation approval
- Auth and Domain Model: N/A for Phase 1 model/auth changes; GO to Security and Permissions assessment (2026-10-15)
- Security and Permissions: reported pre-existing anonymous-write risk; no Phase 1 behavior change identified (2026-10-15)
- PM execution decision: GO EXECUTION for shared-001 Phase 1; shared-004 remains out of scope
- Current phase: Phase 1-only commit authorized; awaiting Implementation Agent
- Phase 0 baseline: verified 2026-10-06; all 11 squash tests passed
- Planning handoff: GO; no blockers
- Phase 1 implementation: completed 2026-10-23; focused route/POST tests passed (7), full squash suite passed (12), no diagnostics
- Reviewer and Challenge: GO to Verification and Release (2026-10-23); only finding is the explicitly transitional 827-line initializer, which remains a required follow-up before final release acceptance
- Verification and Release: GO (2026-10-23); focused tests (7) and full squash suite (12) passed, URL configuration unchanged, rollback procedure clarified
- Planning and Scope: GO to Verification and Release retry (2026-10-23); pre-commit stash preservation and post-commit single-SHA revert are now specified
- Product Manager decision: GO NEXT PHASE for shared-001 Phase 1; authorize a Phase 1-only commit before Phase 2A, with no merge or deployment
- Phase 1 changes remain uncommitted pending the authorized Implementation Agent action
- Pre-cutover baseline tag: `slice2-pre-cutover` at `bc8b437fea8c4acca61f0c3da6ad733daa154a65`
- Next required action: Send the single Phase 1 commit prompt to the Implementation Agent

## Active Working File (Temporary)

- Slice 2 execution file: `backlog/plan/slices/slice-2-execution-temp.md`
- Lifecycle rule: keep while Slice 2 is active; archive or delete after Slice 2 is completed and accepted.

## Active Slice Queue

1. Slice 2: Squash Full Views Refactor
2. Slice 3: Yamb Views Refactor
3. Slice 4: Sjoelen Views Refactor
4. Slice 5: Service Test Coverage
5. Slice 6: Frontend AJAX Toggles
6. Slice 7: Unified Player Model Migration
7. Slice 8: Login/Logout + Invite Flow
8. Slice 9: Permissions + Feature Flags
9. Slice 10: Session Recap + Monitoring

## Session Start Checklist

1. Confirm previous slice closure and active slice.
2. Open the active temporary slice file for execution context.
3. Copy and send the single prompt in "Next Prompt To Send".
4. Continue with "Runbook After Next Output".

## Next Action Required

Implement the approved shared-001 Slice 2 Phase 1 package cutover only. Preserve behavior and the existing security posture; do not implement shared-004 authentication or permission changes.

## PM Decision Note (2026-07-23)

- Decision: `GO ADOPT` for `backlog/plan/WAY_OF_WORKING.md` v2.
- Outcome: governance gate is closed; Slice 2 may continue from planning handoff for Phase 1.

## Reviewer Output (Option B) - 2026-07-23

Findings by severity:

- High: Phase 1 can pass while routes silently regress because current baseline coverage is too narrow. Existing squash tests are mostly leaderboard-focused, so file-to-package import breakage in non-leaderboard views could slip through.
- High: Phase 0 and Phase 1 gates do not require explicit URL-to-view resolution checks and full route smoke checks, which are the primary risks of file-to-package conversion.
- Medium: Commit boundaries are mostly good, but Phase 2 still bundles two responsibilities (matches and players). A split into two commits is safer for review and rollback.
- Medium: Rollback plan is stated but not operationalized. The plan lacks explicit pre-cutover tag, rollback command sequence, and post-rollback smoke verification requirement.
- Medium: Statistics acceptance checks mention context stability but do not define an explicit required context key contract test.

Required plan changes before implementation:

1. Add mandatory pre-cutover smoke tests for all squash endpoints and key GET/POST flows before Phase 1 can begin.
2. Add a Phase 1 gate that verifies URL resolution and view import compatibility explicitly (not only "tests are green").
3. Split current Phase 2 delivery into two commits: 2A matches module, 2B players module.
4. Add explicit rollback runbook steps: pre-cutover tag, revert command, and post-revert smoke checklist.
5. Add a concrete statistics context contract test with a fixed expected key set.

Final recommendation: Block Phase 1 start until required plan updates are applied and acknowledged.

## Reviewer and Challenge Review (2026-10-15)

- Status: GO to Auth and Domain Model impact assessment. This advances the required review chain only; it is not PM approval to implement.
- Findings by severity:
  - Medium: The existing 11-test baseline exercises GET route reachability and POST redirects, but does not prove URL resolver-to-view mapping or the full `views` re-export contract. The Phase 1 plan explicitly requires `reverse()`/`resolve()` checks for every named route and an assertion that the exact 11 URL callables are exposed by `from squash import views`; these remain mandatory before Phase 1 completion.
  - Low: The rollback runbook gives alternatives for recovery after the initial commit revert. Before the merge candidate, record the accepted baseline tag and commit, use commit-level revert as the rollback path, and retain post-rollback smoke validation evidence.
- Evidence: `urls.py` references 11 callables through `.views`; the route smoke test reverses all 11 routes and checks GET responses, while POST tests check redirects. The current module has three module-level relative imports and four function-local `.forms` imports; package relocation requires parent-relative imports for all seven. The plan prohibits behavior extraction in Phase 1 and keeps `urls.py` unchanged. The documented squash suite passed all 11 tests on 2026-10-06; a current rerun was unavailable because Django is not installed in the active Python environment.
- Blockers: None to the Auth and Domain Model handoff. Before Phase 1 completion, the resolver/export checks, existing smoke checks, and full squash suite must pass; create the pre-cutover tag before the merge candidate. Security review and explicit PM `GO EXECUTION` remain required before implementation.
- Next target agent: Auth and Domain Model Agent.
- Required inputs: `backlog/plan/plan.md`, this roadmap, `backlog/plan/slices/slice-2-execution-temp.md`, `backlog/plan/WAY_OF_WORKING.md`, `backlog/to-do/shared-001-refactor-python-code.md`, `yamb_scores/squash/urls.py`, `yamb_scores/squash/views.py`, and `yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py`.

## Auth and Domain Model Impact (2026-10-15)

- Status: N/A for domain model, authentication, or migration changes in Phase 1; GO to Security and Permissions assessment. This is not approval to implement.
- Evidence: The squash models contain no user/account relationship, and the forms operate only on existing squash models. The Phase 1 package relocation changes no schema or data behavior, so no migration is indicated. The views contain no `request.user` checks or local auth/permission decorators. Project settings include `AuthenticationMiddleware` but no global login-required middleware. The separate shared-004 backlog defines anonymous users as read-only and registered/admin users as permitted writers.
- Security handoff note: The current write views appear reachable without a local authentication/permission check, and the project settings show no global login gate. This is a pre-existing access-control concern, not caused by the package move; Security should assess it against shared-004 and keep any remediation out of Phase 1 unless Planning explicitly changes scope.
- Blockers: None to the Security handoff. Security review and explicit PM `GO EXECUTION` remain required before implementation.
- Next target agent: Security and Permissions Agent.
- Required inputs: `backlog/plan/plan.md`, this roadmap, `backlog/plan/slices/slice-2-execution-temp.md`, `backlog/plan/WAY_OF_WORKING.md`, `backlog/to-do/shared-001-refactor-python-code.md`, `backlog/to-do/shared-004-login-system-unified-player-model.md`, `yamb_scores/config/settings.py`, `yamb_scores/config/urls.py`, `yamb_scores/squash/urls.py`, `yamb_scores/squash/views.py`, `yamb_scores/squash/models.py`, `yamb_scores/squash/forms.py`, and `yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py`.

## Security and Permissions Review (2026-10-15)

- Status: BLOCK pending PM execution decision. Security impact introduced by the package-only relocation is N/A; a high-severity pre-existing authorization gap conflicts with shared-004.
- Finding (High): Anonymous users can submit squash mutations. `new_match`, `new_session`, `new_player`, `edit_player`, and `delete_player` have no local authentication/permission checks; the corresponding handlers save or delete model records. `AuthenticationMiddleware` only makes `request.user` available and does not require login, and no global login-required middleware is configured. The smoke tests use Django's unauthenticated test client for these POST flows. Shared-004 explicitly says anonymous users may view data but may not write.
- Scope: This gap predates Phase 1 and is not caused by relocating the intact view module. Do not add auth/permission behavior as part of the package cutover. Planning should decide whether to create or advance a separate security/auth slice before implementation proceeds.
- Blockers: PM must record `GO EXECUTION` with explicit acceptance of the unchanged risk, or `NO-GO` and route the authorization remediation through Planning and Scope. No code implementation is approved by this review.
- Next target agent: Product Manager Agent.
- Required inputs: `backlog/plan/plan.md`, this roadmap, `backlog/plan/slices/slice-2-execution-temp.md`, `backlog/plan/WAY_OF_WORKING.md`, `backlog/to-do/shared-001-refactor-python-code.md`, `backlog/to-do/shared-004-login-system-unified-player-model.md`, `yamb_scores/config/settings.py`, `yamb_scores/config/urls.py`, `yamb_scores/squash/urls.py`, `yamb_scores/squash/views.py`, `yamb_scores/squash/models.py`, `yamb_scores/squash/forms.py`, and `yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py`.

## Product Manager Execution Decision (2026-10-15)

- Decision: `GO EXECUTION` for Slice 2 Phase 1 under `shared-001`; this supersedes the initial `NO-GO` recorded earlier in this review cycle.
- Rationale: `shared-001` authorizes a behavior-preserving views refactor and explicitly leaves models/forms/URLs unchanged; the planning handoff marks login/player work out of scope. The anonymous-write finding is pre-existing, and the package relocation introduces no authorization change. `shared-004` remains out of scope and must not be implemented as part of Phase 1.
- Blockers: None for this scoped refactor. Preserve current behavior and security posture. Existing Phase 1 resolver/export checks, GET/POST smoke tests, full squash suite, and pre-cutover tag precondition remain mandatory.
- Next target agent: Implementation Agent.
- Required inputs: `backlog/plan/plan.md`, this roadmap, `backlog/plan/slices/slice-2-execution-temp.md`, `backlog/plan/WAY_OF_WORKING.md`, `backlog/to-do/shared-001-refactor-python-code.md`, `yamb_scores/squash/urls.py`, `yamb_scores/squash/views.py`, and `yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py`.

## Next Prompt To Send

Copy/paste exactly:

```
You are the Implementation Agent. Create the explicitly authorized Phase 1-only commit for shared-001; do not start Phase 2A in this prompt.

Read:
- backlog/plan/plan.md
- backlog/plan/ROADMAP.md
- backlog/plan/slices/slice-2-execution-temp.md
- backlog/plan/WAY_OF_WORKING.md
- backlog/to-do/shared-001-refactor-python-code.md
- yamb_scores/squash/urls.py
- yamb_scores/squash/views/__init__.py
- yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py

PM authorization and verification evidence:
- PM decision: `GO NEXT PHASE`; an isolated Phase 1-only commit is authorized before Phase 2A. Merge and deployment are not authorized.
- Focused route/POST suite passed 7 tests; full `squash.tests` passed 12 tests; no diagnostics. All 11 route resolver/export checks pass and `squash/urls.py` is unchanged.
- The relocated module differs from the accepted baseline only by the seven required import-depth changes.
- `HEAD` and `slice2-pre-cutover` resolve to `bc8b437fea8c4acca61f0c3da6ad733daa154a65`.
- The rollback runbook specifies reversible pre-commit stash handling and post-commit revert of the recorded Phase 1 SHA.
- The approximately 827-line initializer remains a required extraction before overall refactor completion or final release acceptance.
- Authorized Phase 1 files only: `yamb_scores/squash/views.py` (deletion/rename), `yamb_scores/squash/views/__init__.py`, `yamb_scores/squash/tests/views/test_route_smoke_and_post_flows.py`, `backlog/plan/ROADMAP.md`, `backlog/plan/slices/slice-2-execution-temp.md`, and `backlog/plan/WAY_OF_WORKING.md`.

Handoff:
- Status: GO to execute the authorized Phase 1-only commit.
- Blockers: None for the commit operation. The oversized initializer remains a follow-up before final release acceptance.
- Next target: Implementation Agent.
- Required inputs: the authorized file list, current staged/unstaged diff, verification evidence, rollback runbook, and baseline tag.
- Scope check: shared-001 Phase 1 only. Do not include shared-004 or unrelated work.

Task:
1. Confirm the worktree contains no changes outside the authorized Phase 1 file list. Do not stage or commit anything else.
2. Stage only the authorized files, inspect the staged names and diff, and create one Phase 1-only commit preserving the approved file-to-package cutover and resolver/export tests.
3. Do not merge, deploy, alter application behavior, or start Phase 2A in this prompt.
4. Report the commit SHA and verify `slice2-pre-cutover` remains the parent baseline. Then update the roadmap and active slice with the commit SHA and the single Phase 2A next prompt; do not create a second commit for those follow-up status updates.
5. Keep the oversized initializer explicitly transitional and keep shared-004 and unrelated work out of scope.
```

## Runbook After Next Output

1. Update this file with one clear next action.
2. Update `backlog/plan/slices/slice-2-execution-temp.md` with decisions and phase status.
3. Start only the approved next phase.
4. Run Reviewer gate before moving to the following phase.
5. Keep all execution detail in temporary slice file, not in chat-only memory.
6. Mandatory: steps 1 and 2 are atomic; do not finish a turn with only one file updated.

## Maintenance Rule

- Update only these sections between sessions:
  - Current Session State
  - Active Working File (Temporary)
  - Active Slice Queue (if priorities change)
  - Next Action Required
  - Next Prompt To Send
- Keep the temporary slice file current with implementation notes, findings, and approvals.
- Delete or archive temporary slice file once the slice is complete.
- Completion check: after any status/prompt update, `ROADMAP.md` and the active slice temp file must show the same phase, next action, and next prompt target.
