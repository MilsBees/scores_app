# Definitive Way of Working (v2)

Status: Adopted (PM GO, 2026-07-23)
Scope: All active slices
Owner: Planning Agent + Product Manager

## Purpose

This document is the operational workflow for all slices and phases.
Each completed turn must leave exactly one immediate next action.

## Source-of-Truth Files

- Strategic rules: `backlog/plan/plan.md`
- Session launcher: `backlog/plan/ROADMAP.md`
- Active slice log: `backlog/plan/slices/<active-slice>-execution-temp.md`

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
    - If GO: next target is Product Manager Agent.
11. Product Manager Agent (Phase Decision)
    - Decides `GO NEXT PHASE`, `GO FIXES`, or `NO-GO`.
    - Must leave one immediate next action (`PROMPT` or `DECISION`).

## Handoff Artifact Contract

Each handoff must include all 5 items:

1. Status: `GO`, `BLOCK`, `N/A`, or `DONE`
2. Evidence summary
3. Blockers (or `None`)
4. Next target agent
5. Required inputs for next agent

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
