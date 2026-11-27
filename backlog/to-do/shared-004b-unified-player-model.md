# Unified player model

Part 2 of the login system (follows [`shared-004a`](shared-004a-login-and-write-protection.md)).

### Who

- Admins managing players; all users, indirectly

### What

- Player models are duplicated across Yamb, Squash and Sjoelen. The same person exists up to three times, and there is no link between a player and a login account.

### Why

- One player per person makes managing players simpler and enables "my games" (shared-004c, shared-005).

### Acceptance Criteria

- [ ] A shared `accounts.Player` model with `name` (required) and `user` (optional link to a login account).
  - **Linked player:** has an account and can log in.
  - **Guest player:** just a name (for casual or one-time players), recorded by someone with an account.
- [ ] Existing players are merged by name (case-insensitive) without losing any game or score. A dry-run report of the merges is reviewed by the owner before the real run.
- [ ] Yamb, Squash and Sjoelen use `accounts.Player`. All views, forms, templates, stats and admin work as before.
- [ ] The old per-app player models are removed only after the switch has been verified in production.
- [ ] Every migration is reversible, or has a documented restore-from-backup path, and is tested against a copy of the production database before deploying.

### Notes

- Do this in backward-compatible steps, each deployable on its own: add the new model → backfill and link → switch reads and writes → remove the old models. That likely means several PRs.
- Players don't need an account to take part in a game.
