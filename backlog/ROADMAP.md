# Roadmap

## Goals

- Keep improving the app for all games (Yamb, Squash, Sjoelen), and possibly add more games later.
- Good UX (fast, responsive, simple for non-technical users) and a maintainable codebase (small modules, little duplication, good tests).
- **Make it secure:** anyone can view, but only people who should be allowed to can record, edit or delete data.

## Priorities

1. **Safety first:** no data loss, and minimal downtime (a PythonAnywhere reload takes seconds; always back up the DB before a deploy that migrates).
2. Then user experience.
3. Then code cleanliness.

There are no deadlines; this is a hobby project worked on in bursts.

## Now

1. [`shared-006`](to-do/shared-006-test-safety-net.md): Test safety net: smoke tests for every route in every app, plus a registry of write URLs
2. [`shared-007`](to-do/shared-007-production-hardening.md): Production settings hardening
3. [`shared-004a`](to-do/shared-004a-login-and-write-protection.md): Login page, and require login for every write action

## Next

4. [`shared-004b`](to-do/shared-004b-unified-player-model.md): Unified player model
5. [`shared-004c`](to-do/shared-004c-ownership-permissions.md): Ownership-based edit and delete permissions
6. [`shared-004d`](to-do/shared-004d-invite-registration.md): Request login and invite registration
7. [`shared-001`](to-do/shared-001-refactor-python-code.md): Finish splitting the views (squash → yamb → sjoelen, one PR per app)

## Later

- [`shared-003`](to-do/shared-003-improve-statistics-speed.md): Statistics speed and instant toggles
- [`yamb-003`](to-do/yamb-003-investigate-game-vs-scoresheet-model-overlap.md): Investigate the Yamb Game vs Scoresheet overlap
- [`yamb-002`](to-do/yamb-002-submit-from-scoresheet.md): Submit a game straight from the scoresheet
- [`shared-002`](to-do/shared-002-games-over-time-ytd.md): YTD "games over time" graphs
- [`shared-005`](to-do/shared-005-create-user-page.md): User profile page (needs shared-004)

## Why this order

Security is the main goal, so it comes first. The tests come before it so the auth change can be proven not to break anything, and so there's one test that checks *every* write URL rejects anonymous users. The login requirement (004a) is a small change in each view and doesn't wait for the bigger player-model migration or the views refactor.
