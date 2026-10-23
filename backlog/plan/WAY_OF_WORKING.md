# Definitive Way of Working (v2)

Status: Adopted (PM GO, 2026-07-23)
Scope: All active slices
Owner: Planning Agent + Product Manager

## Purpose

This document is the operational workflow for all slices and phases.
Each completed turn must leave exactly one immediate next action.

## Code Readability and Module Size Rule (Mandatory)

- Code delivered by a slice must remain readable and followable by a human; passing tests or moving code between files does not by itself satisfy maintainability goals.
- Python view modules should be split into cohesive, responsibility-focused modules and target no more than 200 lines, consistent with the strategic success criteria in `backlog/plan/plan.md`.
- Keep package `__init__.py` files focused on lightweight setup and compatibility re-exports; do not use them to hide an oversized implementation module.
- A phase may temporarily preserve an oversized module only when the approved active slice explicitly describes a behavior-preserving transitional step, names the follow-up extraction phase(s), and records why extraction is deferred. This exception is phase-scoped, not an end-state waiver.
- Reviewers must assess readability, cohesion, and module size as well as behavior and test results. A transitional exception must be reported as such; it does not satisfy overall refactor completion or final release acceptance until the planned extraction target is met.

## Source-of-Truth Files

- Strategic rules: `backlog/plan/plan.md`
- Session launcher: `backlog/plan/ROADMAP.md`
- Active slice log: `backlog/plan/slices/<active-slice>-execution-temp.md`

## Single-Item Scope Rule (Mandatory)

- Each active execution phase works on exactly one identified backlog item. The Product Manager and Planning Agent must record its ID, in-scope work, out-of-scope work, and acceptance checks in the active slice context.
- At every handoff, agents compare findings and proposed work against that active item. Classify each material finding as in-scope, a demonstrated direct dependency, or unrelated/out-of-scope.
- An unrelated or out-of-scope finding must be documented and routed for separate Product Manager/Planning triage. By itself, it does not expand or block the active item.
- An agent who believes an out-of-scope issue blocks the active item must explain the concrete dependency or the affected acceptance criterion/non-negotiable and request a Product Manager decision. Agents do not change scope or authorize cross-item work themselves.
- Any approved scope change returns to Planning to update the backlog coverage, acceptance checks, active slice, and next prompt before implementation continues.
- Implementation Agents work only on the approved item and phase. Work from another backlog item requires explicit Product Manager approval and updated planning records.

## Canonical Handoff Chain (Authoritative)

This chain is mandatory. No agent is skipped. 

1. Product Manager Agent (Intake)
   - Confirms active slice, phase scope, and backlog coverage.
   - Next target: Planning and Scope Agent.
2. Planning and Scope Agent (Phase Plan)
   - Defines acceptance checks, boundaries, and phase prompt.
   - Next target: Architecture and Refactor Agent.
3. Architecture and Refactor Agent (Design Review)
   - Validates module boundaries, compatibility risk, and rollback shape.
   - Next target: Reviewer and Challenge Agent.
4. Reviewer and Challenge Agent (Pre-Implementation Review)
   - Challenges plan and architecture with GO/BLOCK.
   - If BLOCK: back to Planning Agent (and Architecture Agent if needed), then repeat Step 4.
   - If GO: next target is Auth and Domain Model Agent.
5. Auth and Domain Model Agent (Domain Impact)
   - Returns impact assessment or explicit `N/A` with reason.
   - Next target: Security and Permissions Agent.
6. Security and Permissions Agent (Security Gate)
   - Returns security findings or explicit `N/A` with reason.
   - Next target: Product Manager Agent.
7. Product Manager Agent (Execution Decision)
   - Decides `GO EXECUTION` or `NO-GO`.
   - If `GO EXECUTION`: next target is Implementation Agent.
8. Implementation Agent (Build)
   - Implements approved phase only and runs required tests.
   - Next target: Reviewer and Challenge Agent.
9. Reviewer and Challenge Agent (Post-Implementation Review)
   - Reviews code/tests with GO/BLOCK.
   - If BLOCK: back to Implementation Agent, then repeat Step 9.
   - If GO: next target is Verification and Release Agent.
10. Verification and Release Agent (Evidence Gate)
    - Confirms tests, rollback readiness, and go/no-go recommendation.
    - If BLOCK: back to Implementation Agent or Planning Agent (if scope is unclear).
   - If GO: next target is Human Verification and Acceptance when the gate applies; otherwise record N/A and the reason, then hand off to Product Manager Agent.
11. Human Verification and Acceptance (Product Owner)
   - Required before the next phase, merge, or release when a change can affect user-visible pages, navigation, UI behavior, or an end-to-end workflow. This includes refactors of routed views even when behavior is intended to remain unchanged.
   - Product Manager provides a local run command, exact pages/workflows to check, and expected results. The user runs the app locally and responds `GO`, `FIXES`, or `NO-GO`.
   - If `FIXES`: return to Implementation Agent with the observed issue. If `NO-GO`: return to Product Manager/Planning for a decision. If `GO`: next target is Product Manager Agent for the phase decision.
   - Do not advance to another phase, merge, or release until the user explicitly returns `GO`.
   - Mark N/A only for changes with no user-visible or runtime workflow impact; record the rationale and supporting automated evidence in both planning files.
12. Product Manager Agent (Phase Decision)
    - Decides `GO NEXT PHASE`, `GO FIXES`, or `NO-GO`.
    - Must leave one immediate next action (`PROMPT` or `DECISION`).

## Human Verification Prompt Requirements

- The Product Manager's human-verification prompt must be copy/paste-ready and mirrored in the roadmap and active slice.
- Include the local startup command, local URL, specific pages/workflows, and a short expected-result checklist. Reuse repository setup instructions and avoid production data or irreversible mutations.
- Ask for one explicit response: `GO`, `FIXES` with observed details, or `NO-GO`.
- Keep the phase status at human verification pending until the user responds. A green test suite or reviewer signoff does not substitute for this gate.

## Handoff Artifact Contract

Each handoff must include all 6 items:

1. Status: `GO`, `BLOCK`, `N/A`, or `DONE`
2. Evidence summary
3. Blockers (or `None`)
4. Next target agent
5. Required inputs for next agent
6. Scope check: active backlog item, whether the finding/work is in scope, and any demonstrated direct dependency or separate out-of-scope follow-up

Missing any item means handoff is invalid.

## Immediate Action Contract

At end of every turn, exactly one of these must exist and be file-recorded:

1. `PROMPT`: one copy/paste prompt under `Next Prompt To Send`
2. `DECISION`: one explicit PM decision request (GO/NO-GO or fixed options)

Recording rule:
- The single next action is stored in `backlog/plan/ROADMAP.md` and mirrored in the active slice temp file.
- Chat output may summarize the next action, but chat is never the source of truth.

Forbidden state: neither exists.

## Atomic Sync Protocol

When phase, status, next action, or next prompt/decision changes:

1. Update `backlog/plan/ROADMAP.md`.
2. Update active slice temp file in the same turn.
3. Verify these two files match on:
   - current phase/gate,
   - next required action,
   - next prompt/decision target.

A turn is incomplete until both files match.

## Drift Recovery

If roadmap and slice temp drift:

1. Pause new implementation work.
2. Repair both files first.
3. Add a dated Decision Note in slice temp.
4. Resume only after sync is restored.

## End-of-Turn Checklist

- `Current Session State` updated in roadmap.
- `Live Execution Log` updated in active slice temp.
- Exactly one immediate action exists (`PROMPT` or `DECISION`).
- No conflicting next action between files.
