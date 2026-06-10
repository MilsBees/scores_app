# Delivery Roadmap: Backend Refactor + Unified Login (Option A)

## Master Roadmap: Full Delivery Plan

### Phase 1: Backend Refactor (~70 work days)

**Goal:** Clean, testable service layer across all three apps. Fixes performance bottlenecks.

#### Slice 1: Squash Leaderboard Query Optimization (CURRENT)
- **Work Days:** 3-4 days
- **What You're Doing:** Extract leaderboard stats into service, add tests, verify query count drops 90%
- **Status:** Ready to start ✅
- **Blocker:** None

#### Slice 2: Squash Full Views Refactor
- **Work Days:** 8-10 days
- **What You're Doing:** Split `views.py` into matches/players/statistics/h2h files. Extract all calculations into services.
- **Status:** Blocked until Slice 1 done (pattern established)
- **Dependency:** Slice 1 complete + Reviewer Agent sign-off

#### Slice 3: Yamb Views Refactor
- **Work Days:** 6-8 days
- **What You're Doing:** Split views.py (two game systems), extract services
- **Status:** Blocked until Slice 2 done
- **Dependency:** Slice 2 complete

#### Slice 4: Sjoelen Views Refactor
- **Work Days:** 5-7 days
- **What You're Doing:** Split views.py, fix stdev/min/max calculations via Django annotations
- **Status:** Blocked until Slice 3 done
- **Dependency:** Slice 3 complete

#### Slice 5: Add Test Coverage (Unit Tests for All Services)
- **Work Days:** 4-5 days
- **What You're Doing:** Write pytest/unittest for all service functions across squash/yamb/sjoelen
- **Status:** Can run in parallel with Slice 4 (Test Agent works separately)
- **Target:** ≥80% coverage on services

#### Slice 6: Frontend AJAX Toggles (Set-Type Buttons)
- **Work Days:** 3-4 days
- **What You're Doing:** Convert Overall/11-point/21-point toggle buttons to AJAX (no page reload)
- **Status:** Can run in parallel with Slices 3-5 (frontend independent)
- **Impact:** Users see instant toggle response (major UX improvement)

---

**Phase 1 Total:**
- **Work Days:** ~35-45 days

---

### Phase 2: Unified Auth System (~30 work days)

**Goal:** Unified Player model, login system, permissions.

#### Slice 7: Unified Player Model Migration
- **Work Days:** 5-6 days
- **What You're Doing:** Create accounts app, migrate data, update all FK references
- **Status:** Blocked until Phase 1 complete (refactor provides clean architecture for auth)
- **Risk:** High (data migration), so Verification Agent reviews thoroughly

#### Slice 8: Login/Logout Views & Forms
- **Work Days:** 3-4 days
- **What You're Doing:** Django auth views, invite system, registration form

#### Slice 9: Permissions & Feature Flags
- **Work Days:** 3-4 days
- **What You're Doing:** Implement view permissions (anonymous = read-only, registered = read/write), feature flags for gradual rollout

#### Slice 10: Session Recap & Monitoring
- **Work Days:** 1-2 days
- **What You're Doing:** Planning Agent prepares session recap docs in chat; Verification Agent monitors for issues

---

**Phase 2 Total:**
- **Work Days:** ~15-20 days

---

### Phase 3: Optional Future Work

These depend on Phase 1 + 2 being complete. Create new backlog items as needed:

- **User Profile Pages:** Let users see their stats across all games
- **Frontend Framework Evaluation:** If performance still not satisfactory, evaluate Svelte
- **Advanced Stats:** YTD games tracking, seasonal breakdowns
- **Integration Tests:** Add after unit tests established

---

## Work Session Schedule (Your Hobby Pattern)

Example rhythm (2-3 sessions/week, 2-3 hours/session):

**Week 1:**
- Mon (2h): Session kickoff recap + Slice 1 planning + start extraction
- Wed (3h): Continue service extraction, start tests
- Fri (2h): Finish tests, verify query count, commit

---

## Work Session Rhythms

Each work session follows the same pattern regardless of when you work:

**Session Duration: 2-3 hours (typical)**

1. **Context loading (5-10 min):** Planning Agent recaps last session status
2. **Implementation (90-150 min):** Write code, run tests locally
3. **Review & commit (15-30 min):** Reviewer Agent feedback, fix issues, commit

Each slice typically needs 5-8 sessions to complete (depending on complexity).

---

## What One Work Session Looks Like

### Example: Slice 1 Session 2

**Minute 0-5:** Context loading
```
Planning Agent provides recap:
  - Last session: finished squash query extraction
  - This session: write tests for get_leaderboard_stats()
  - Success = 3 test cases written + all pass locally
```

**Minute 5-120 (115 min):** Implementation
```
You implement:
  - Test file: squash/tests/test_stats.py
  - 3-4 test cases
  - Run pytest, debug failures
  - Refine code based on test feedback
```

**Minute 120-150 (30 min):** Review & commit
```
You request Reviewer Agent review
  - Run git diff, show code
  - Reviewer Agent critiques (blind spot check)
  - Fix any issues
  - Commit to local branch
```

**Session End:**
- Close VS Code
- Code sits on your local branch until next session
- Zero pressure to "keep running"

---

## Effort Breakdown by Activity

### Typical Slice (10 work days):

| Activity | Time | Sessions | Notes |
|----------|------|----------|-------|
| Planning & code review | 1.5 days | 1 session | Plan Agent + your approval |
| Implementation (code) | 5 days | 2-3 sessions | Write new code, run tests locally |
| Testing (unit tests) | 2.5 days | 1-2 sessions | Test Implementation Agent helps |
| Review & refinement | 1 day | 1 session | Reviewer Agent finds issues, you fix |
| Total | 10 days | 5-7 sessions @ 2-3 hrs ea | 10-20 hours total |

---

## Handling Gaps Between Sessions

No matter how long the gap (days, weeks, months), resuming is simple:
- Planning Agent provides recap: "Last session: completed Slice 1. This session: begin Slice 2."
- Chat history shows exactly where you were
- No lost work (all on git)
- No re-reading code (agents recap)

**Session recaps make sporadic work sustainable.**

---

## Risk Mitigations

### Risk: "I work sporadically, what if I forget where I am?"
**Mitigation:** Session kickoff recap in chat. Planning Agent loads context automatically.

### Risk: "What if I take a 3-month break?"
**Mitigation:** Slices are merged to git. Branch persists. Chat history persists. You can resume mid-slice or start fresh with next slice.

### Risk: "What if code breaks between sessions?"
**Mitigation:** Verification Agent tests all code before merge. Git branches isolate broken code. Rollback is one command.

---

## Next Session: Getting Started on Slice 1

When you return, use this prompt to resume implementation:

```
You are the Implementation Agent. You're beginning Slice 1: Squash Leaderboard Query Optimization.

Read the delivery plan at backlog/plan/plan.md and ROADMAP.md for context.
Focus on Slice 1 acceptance criteria:
- Extract statistics calculations from squash/leaderboard view into squash/services/stats.py
- Function: get_leaderboard_stats(set_type_filter=None) returns relative_stats + absolute_stats
- Use prefetch_related/select_related (verify query count: current ~150-500 → target ≤15)
- Add unit tests: ≥80% coverage
- Backward-compatible: views/__init__.py re-exports old function names

Your first task: 
1. Analyze current squash/views.py leaderboard function (lines 134-200)
2. Extract the calculation logic into squash/services/stats.py
3. Create get_leaderboard_stats() function
4. Update leaderboard view to call this function
5. Run Django shell to verify query count drops

Work in small, reviewable commits. When done with this step, request Reviewer Agent feedback.
```

---

## Session Wrap-Up Checklist

- [x] Roadmap reordered: Squash → Yamb → Sjoelen (priority order)
- [x] Calendar dates removed (work days only)
- [x] All 10 slices defined with work day estimates
- [x] Phase 1 + Phase 2 totals calculated
- [x] Risk mitigations documented
- [ ] Next session prompt ready (copy the prompt above when returning)
- [ ] Approve this roadmap and begin Slice 1 on your next session
