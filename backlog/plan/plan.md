# Delivery Plan: Refactor + Unified Login

This document is for planning only. No backlog item implementation starts until this plan is refined and explicitly approved.

## Requirements Input (To Be Filled By You)

Use this section to define exactly what we should deliver.

### Objective
- Primary outcome: We slowly want to keep improving the app for all existing games (i.e. squash, yamb, sjoelen), though we may also want to add more games in the future. 
- Secondary outcome(s): Almost as important as added functionality of the app is the ease of use, both in terms of the user experience of the app as well as the code base itself. That means the app should be fast, efficient and responsive, following the best practices. At the same time, the code should be organized well with minimal duplicate code, adequate testing and maintanable file sizes. 

### Scope (In)
- Pretty much everything is fair game. In fact, you initially created this document for the python refactor and the unified login system, but in the end this document should cover all improvements to the app. 

### Out of Scope (For Now)
- CI/CD isn't necessary for now. The release flow as is works fine, where we upload our code to Gitlab and I manually update the code on the pythonanywhere server. 

### Constraints
- Technical constraints: I am not the most technical person so don't have the ability to review your code in such a way that I can actually catch mistakes besides viewing the locally run app and pointing out things in the user experience. Therefore, agents should review and test each other's work. 
- Time constraints: We don't have any deadlines necessarily, but as this is a hobby project, I will only be working on this every once in a while. 
- Team/process constraints: As I will go through periods where I'm working on this project less (or more), each session will start of a reminder of where we left off and what's on the agenda. 

### Success Criteria
- Functional success: All current features continue to work and anything new works well also. 
- Quality success (tests, maintainability, performance): (1) Test coverage exists for all critical paths (auth, data mutations, migrations); (2) All `views.py` files are split into logical modules ≤200 lines; (3) No code duplication across apps for shared patterns; (4) Statistics/filtering queries complete in <500ms (measured from slow pages); (5) Response time for list/detail pages improves or stays same post-refactor.
- Rollout success (migration safety, zero/low downtime): (1) All migrations are reversible and tested on production data; (2) Zero downtime deployment possible (blue-green or feature flags); (3) Zero data loss; (4) Rollback plan documented and practiced; (5) User-facing features behind toggles until fully tested.

### Risks You Already See
- I've already noticed that certain aspects of the app are quite slow and inefficient, flow pages reloading when changing the scope of our data for the statistics pages to unmaintanable code.
- I fear that the app is already at a kind of tipping point where it's quite large and we should refactor before it's too late and it becomes difficult to do without significant downtime. 
- Therefore, we should look to make changes now in a way that is future proof and will mean that the app growing isn't a problem for performance or functionality. 

### Decision Preferences
- Delivery style: Generally we should go safety first as we have no deadlines and are in no rush.
- Refactor depth: Needs dependent, but as we want to refactor in such a way that the app will be robust for a long time to come, I lean towards deeper if that's what's necessary. 
- Migration approach: Phased seems safer, but I defer to your experience here as well. You can give your recommendations and I will okay them. 

### Non-Negotiables
- At no point should we have downtime. The app is very much in use at the moment and we do not want to lose any of our data or have downtime in the app. 

---

## Initial Proposal: Agent Team and Roles

The goal is to use multiple specialized agents with explicit review gates so changes are challenged before implementation moves forward.

### 1) Planning and Scope Agent
- Focus: turn your requirements into milestones and acceptance checks.
- Inputs: backlog items, constraints, success criteria.
- Outputs: execution slices, dependency map, definition of done per slice.
- Checks by others: challenged by Architecture Agent and Risk Agent.
- My notes: You are free to suggest new backlog items especially when it comes to backend things. 
- Additional workflow rule: All requests are owned first by Planning + Product Manager for intake, scope, and backlog triage before any implementation starts.

### 2) Architecture and Refactor Agent
- Focus: code structure, module boundaries, maintainability decisions.
- Inputs: current app structure, refactor backlog item.
- Outputs: proposed target layout for views/services/forms and migration-safe refactor sequence.
- Checks by others: reviewed by Reviewer Agent for over-abstraction and regression risk.
- My notes: We don't need to stay within the box of doing our frontend in javascript and html. If a migration to another frontend framework (e.g. svelte) makes sense for performance or maintainability, that should outweigh considerations of amount of work. 

### 3) Auth and Domain Model Agent
- Focus: unified Player model and login/invite flow design.
- Inputs: unified login backlog item and permission matrix.
- Outputs: data model proposal, migration strategy, access-control rules.
- Checks by others: challenged by Security Agent and Verification Agent.
- My notes: None for now. 

### 4) Security and Permissions Agent
- Focus: authorization correctness and abuse prevention.
- Inputs: role matrix, invite flow, edit/delete ownership rules.
- Outputs: threat checklist, permission edge cases, hardening recommendations.
- Checks by others: validated by Verification Agent with explicit scenario tests.
- My notes: This should be continuous and will become especially important as our user base grows following the login system. 

### 5) Implementation Agent
- Focus: execute approved slices only, with small and reviewable diffs.
- Inputs: approved plan slice and acceptance criteria.
- Outputs: code changes, migration files, and concise implementation notes.
- Checks by others: always blocked on Reviewer Agent signoff before merge-ready status.
- My notes: Perhaps we should add a second implementation agent that focuses on writing software tests, which we don't have as of yet. 

### 6) Reviewer and Challenge Agent
- Focus: independent critical review to catch blind spots.
- Inputs: implementation diffs and acceptance criteria.
- Outputs: findings by severity, required fixes, and signoff status.
- Checks by others: unresolved findings escalated to Planning Agent decision log.
- My notes: This agent should really remain neutral and shouldn't be influenced by others, going in fresh each time. 

### 7) Verification and Release Agent
- Focus: testing, rollout safety, and rollback readiness.
- Inputs: final diffs, migration scripts, permission cases.
- Outputs: test evidence, rollout checklist, rollback steps, go/no-go recommendation.
- Checks by others: Planning Agent confirms acceptance criteria are met.
- My notes: This is the agent that is the final gatekeeper before me. In regards to code though, this agent will be the last line of defense. 

### 8) Product Manager Agent
- Focus: Reading this document and ensuring we stick to the plan. 
- Inputs: Checking with me (the primary stakeholder) to see if we are remaining on task and focused. 
- Outputs: Ensuring all other agents are doing what they should be doing.
- Checks by others: Each other agent may have push back on the product manager to ensure minimal mistakes. That way we have an extra level of insurance that we are staying on track and following our objectives. 
- Additional workflow rule: For every request, Product Manager first confirms backlog coverage. If no suitable item exists, Product Manager asks Planning Agent to create one before Implementation Agent starts coding.

---

## How Agents Keep Each Other in Check

### Mandatory Review Gates
1. No slice starts implementation before Planning Agent marks scope and acceptance criteria complete.
2. No data model/auth change proceeds without Security Agent review.
3. No slice is considered done without Reviewer Agent findings resolved or explicitly accepted.
4. No merge-ready status without Verification Agent test and rollback checklist.
5. All requests must go through Planning + Product Manager intake and backlog triage before any implementation proposal.

### Conflict Resolution
1. If two agents disagree, capture the decision in the Decision Log.
2. Product Manager Agent (you) makes final call based on priorities (safety-first, then UX, then code cleanliness).
3. High-risk disagreements (especially those affecting zero-downtime constraint) default to safety-first until you explicitly approve otherwise.

---

## Working Cadence

### Planning Phase
1. **Kickoff**: finalize requirements section and lock agent roles.
2. **Shape**: Planning + Architecture + Auth agents produce first plan slices.
3. **Challenge**: Reviewer + Security agents critique plan in isolation.
4. **Finalize**: update plan based on critiques and lock version for implementation.

### Implementation Phase (Per Slice)
1. **Session Start**: Product Manager loads context (what was done last session, what's on deck).
2. **Slice Prep**: Planning Agent readies next slice with acceptance criteria.
3. **Build**: Implementation Agents (code + tests) work on approved slice in parallel if possible.
4. **Review**: Reviewer Agent does independent challenge pass.
5. **Verify**: Verification Agent checks tests, migration safety, and gives go/no-go.
6. **Merge**: Once Verification approves, code is merged (still no deploy yet).
7. **Session End**: Document decisions, blockers, and next slice priorities in Decision Log.

### Release Phase (When Ready)
1. Verification Agent confirms all slices pass go/no-go.
2. Product Manager approves release window.
3. Verification Agent walks through rollback scenario and confirms downtime is zero.
4. Deploy with rollback plan at-hand.

---

## Decision Log

- Decision 001: Use multi-agent review gates before coding.
- Decision 002: Keep planning and implementation as separate phases.
- Decision 003: Add a dedicated Test Implementation Agent to write tests alongside feature code (since test coverage currently absent).
- Decision 004: Zero-downtime is non-negotiable; all release strategies must support blue-green or feature-flag rollout.
- Decision 005: Product Manager (you) holds final approval on conflicts and release decisions.
- Decision 006: Architecture Agent should provide refactor order options with pros/cons for PM approval.
- Decision 007: Performance baseline on stats pages is first critical task; Planning Agent will create backlog items to address bottlenecks.
- Decision 008: Start with unit tests; integration tests deferred to later stage.
- Decision 009: Prefer strict cutover on auth migration if low-risk; Planning Agent to assess and recommend.
- Decision 010: Session recaps provided in chat (not as files) for sporadic work pattern. 

---

## Resolved Questions

1. **Refactor order**: Planning Agent to provide three refactor order options (backend-first vs. auth-first vs. frontend-first) with pros/cons analysis; PM will choose.
2. **Frontend framework**: Performance and speed are paramount. Concrete blocker: page toggles on stats/leaderboard reload entire page when they should be instant (most modern web apps achieve this). Architecture Agent to evaluate current bottleneck (backend query speed, frontend rendering, or both) and recommend framework migration only if it solves the root cause.
3. **Performance baseline**: Yes, measure stats pages now (baseline before refactor). Planning Agent to create backlog items for identified bottlenecks, reviewed by PM.
4. **Test strategy**: Start with unit tests (models/services). Integration tests deferred to later stage.
5. **Migration layers**: Preference is strict cutover on auth rollout, but Planning Agent should assess risk and recommend safeguards (e.g., rollback safety, feature flags).
6. **Sporadic work**: Session recaps provided in chat at session start (not as files in repo).
7. **Measurement**: Agents to suggest key metrics (beyond test coverage and query speed). PM to approve. 

---

## Zero-Downtime Release Strategy

Since downtime is non-negotiable, every slice must follow one of these patterns:

1. **Backward-compatible migration**: Old and new code coexist; deploy old code first, then new code. Rollback is old-code-only redeploy.
2. **Feature flag**: New behavior is behind a flag. Deploy with flag off, test, then toggle on in prod without redeploy.
3. **Blue-green**: Run two parallel app instances; switch traffic via load balancer. Old instance stays live as instant rollback.

**Verification Agent must confirm which strategy applies to each slice before it ships.**

---

## Product Manager Session Kickoff Template

Use this at the start of each work session:

- Last session ended at: [slice #]
- Completed and merged: [list]
- Blockers from last time: [any unresolved issues]
- On deck for this session: [next 1-2 slices]
- Time available: [rough hours]
- New constraints or changes: [any new info]

---

## Planning Agent Kickoff Task

The Planning Agent's first job is to produce the **Execution Plan** that breaks this delivery plan into concrete, sequenced slices ready for implementation.

### What Planning Agent Must Deliver:

1. **Refactor Order Analysis** (3 options with pros/cons):
   - Option A: Backend refactor first (views → services), then auth, then frontend
   - Option B: Auth first (establishes permissions model), then backend refactor, then frontend
   - Option C: Frontend baseline first (measure current perf), then auth, then backend refactor
   - Include: timeline estimate, risk level, dependencies, and rollback complexity for each

2. **Performance Baseline Report**:
   - Measure current response times on: squash leaderboard, squash statistics, sjoelen statistics, yamb game list
   - Identify root cause of slowness: database queries, template rendering, frontend rendering, or all three
   - Prioritize: which pages need fixing most urgently

3. **Initial Backlog Items** (from performance baseline):
   - Create 3-5 new backlog items for identified performance issues
   - Each item includes: acceptance criteria, estimated complexity, blocker dependencies
   - Sequenced in refactor order chosen by PM

4. **Execution Slice 1** (First actionable slice):
   - Definition of done (testable acceptance criteria)
   - Success criteria (specific, measurable outcomes)
   - Dependencies on other slices (if any)
   - Suggested zero-downtime strategy (blue-green, feature flag, or backward-compatible)

### When to Start Planning Agent:

Write a chat prompt that invokes Planning Agent and includes this plan document. Example structure:

```
You are the Planning Agent. Read the attached Delivery Plan document, which includes:
- Requirements, objectives, and constraints from the Product Manager
- Decision Log with priorities (safety-first, zero-downtime mandatory)
- Resolved questions about refactor order, performance baseline, and test strategy

Your first task is to analyze the app and produce:
1. Three refactor order options (backend-first, auth-first, frontend-first) with pros/cons
2. Performance baseline report (measure slow pages, identify root causes)
3. Create 3-5 new backlog items for performance fixes
4. Define Execution Slice 1 with acceptance criteria and zero-downtime strategy

Refer to the backlog items in shared-001-refactor-python-code.md for refactor context.
Use the existing codebase (yamb, squash, sjoelen apps) to inform your analysis.
```

---

## Execution Plan & Roadmap

**Planning Agent has delivered:**

1. ✅ **Refactor Order Analysis** → Chose **Option A: Backend-First** (safest, aligns with refactor backlog)
2. ✅ **Performance Baseline Report** → Root causes identified
3. ✅ **Initial Backlog Items** → 5 items (Backend-001/002/003, Frontend-001, Auth-001)
4. ✅ **Execution Slice 1** → Squash Leaderboard Query Optimization approved
5. ✅ **Full Roadmap** → See [ROADMAP.md](ROADMAP.md)

**Key Updates to Roadmap:**
- Reordered: Squash → Yamb → Sjoelen (by priority)
- Removed calendar dates (work days only)
- Ready for next session: see "Next Session" section in ROADMAP.md

---

## Current Delivery Status (PM Update)

### Slice 1 Status: Completed

Completed outcomes:
- Leaderboard statistics extracted to `squash/services/stats.py`
- Leaderboard view calls the extracted service
- Query count validated below target (<=15 target, measured lower)
- Unit tests added for service behavior and query count
- Regression fix added for "Last match" sorting and covered by view tests

### Next Active Slice: Slice 2

Slice 2 remains the next priority:
- Split `squash/views.py` into focused modules
- Continue extracting calculation logic into services
- Preserve URL compatibility via `views/__init__.py` re-exports

### Effort Estimation Note

- Slice 1 was completed faster than the original estimate.
- Do not fully re-estimate all slices from one data point.
- Recalibrate estimates after Slice 2 planning with confidence ranges (optimistic / likely / conservative).

---

## Agent Handoff Order (Per Slice)

1. **Product Manager Agent**: confirms slice scope and success criteria
2. **Planning Agent**: produces implementation phases and test gates
3. **Implementation Agent**: executes phases in small commits
4. **Reviewer Agent**: independent findings and sign-off
5. **Verification & Release Agent**: go/no-go + rollback checklist
6. **Product Manager Agent**: final release decision

---

## Release Decision Policy

Because downtime is non-negotiable, each completed slice follows this decision:

1. **Commit + push after reviewer sign-off**
2. **Run Verification & Release Agent checklist**
3. **Release only after PM approval**
4. **If uncertain, defer release and batch with next validated slice**

For Slice 1 specifically:
- Commit/push is appropriate now.
- Production release is allowed only after Verification & Release Agent go/no-go and PM approval.

---

## Ready to Begin Implementation

- [x] All planning complete
- [x] Slice 1 approved and implemented
- [x] Roadmap finalized with work day estimates
- [x] Next session prompt prepared in ROADMAP.md
- [ ] Begin Slice 2 planning in next session (use prompt from ROADMAP.md)
