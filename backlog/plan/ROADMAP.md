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
- Current phase: Slice 2 Phase 1 Architecture and Refactor review
- Phase 0 baseline: verified 2026-10-06; all 11 squash tests passed
- Planning handoff: GO to Architecture and Refactor Agent; no blockers to design review
- Next required action: Send the single Architecture and Refactor Agent prompt below

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

Run Architecture and Refactor review for Slice 2 Phase 1 under the adopted way-of-working.

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

## Next Prompt To Send

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
