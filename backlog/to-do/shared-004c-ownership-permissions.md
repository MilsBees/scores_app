# Ownership-based permissions

Part 3 of the login system (needs [`shared-004b`](shared-004b-unified-player-model.md)).

### Who

- Registered users and admins

### What

- After shared-004a, any logged-in user can edit or delete anything. Users should only be able to change games they took part in.

### Why

- Limits the damage from mistakes or misuse, and makes it clear who may change what.

### Acceptance Criteria

| Action | Anonymous | Registered user | Admin |
|--------|-----------|-----------------|-------|
| View leaderboards, statistics, game history | ✅ | ✅ | ✅ |
| Record new games or matches (can include guest players) | ❌ | ✅ | ✅ |
| Edit or delete games their linked player took part in | ❌ | ✅ | ✅ |
| Edit or delete any game | ❌ | ❌ | ✅ |
| Create guest players (when recording games) | ❌ | ✅ | ✅ |
| Edit or delete players | ❌ | ❌ | ✅ |
| Request a login | ✅ | ❌ | ❌ |

- [ ] Every row in this table is covered by tests, for each app.
- [ ] Edit and delete buttons only show for users who are allowed to use them.
- [ ] Forbidden actions return a clear "not allowed" response and change nothing.
