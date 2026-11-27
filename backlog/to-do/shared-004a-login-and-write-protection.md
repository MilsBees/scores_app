# Login page and write protection

Part 1 of the login system. The full design (including the access-control table) is in [`shared-004b`](shared-004b-unified-player-model.md), [`shared-004c`](shared-004c-ownership-permissions.md) and [`shared-004d`](shared-004d-invite-registration.md).

### Who

- All users. Anonymous visitors can still view everything.
- Regular players (including non-technical ones) who record scores

### What

- Today anyone on the internet can create, edit and delete games, scoresheets, matches and players. There are no authentication checks on any write view.

### Why

- Stops anyone who isn't allowed from changing or deleting data. This is the main security goal.
- Ships on its own, before the bigger player-model migration, so the hole closes early.

### Acceptance Criteria

- [ ] Anonymous users can still view leaderboards, statistics, game history and rules.
- [ ] Every create, edit and delete page and action in Yamb, Squash and Sjoelen requires a logged-in user. Anonymous users are sent to the login page and returned to where they were afterwards.
- [ ] A test built on the shared-006 write-URL registry asserts that an anonymous GET or POST to **every** write URL is rejected and changes nothing in the database.
- [ ] There's a simple, friendly login page (username + password, plus "remember me" so phones stay logged in for a long time) and a logout link. No Django admin is needed for normal users.
- [ ] The header shows who is logged in. "New game" and similar buttons are hidden or point to login for anonymous users.
- [ ] The owner can create accounts for players without them ever touching Django admin (the owner uses admin, or a small management command). This is temporary until shared-004d adds invites.
- [ ] Login attempts are rate-limited (reuse the approach from the wedding login).

### Notes

- In this step, any logged-in user can write. Finer-grained "only your own games" rules come in shared-004c.
- Depends on shared-006 (write-URL registry) and shared-007 (secure cookies / secret key).
