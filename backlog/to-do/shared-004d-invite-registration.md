# Request a login and register by invite

Part 4 of the login system (needs [`shared-004b`](shared-004b-unified-player-model.md)).

### Who

- New users who want to record scores; the owner as admin

### What

- In shared-004a the owner creates every account by hand. New users should be able to ask for access and register themselves through an invite.

### Why

- Less manual work for the owner, and users choose their own password.

### Acceptance Criteria

- [ ] An anonymous user can request a login from the home page (name plus an optional message).
- [ ] The admin sees requests and can generate an invite for one, optionally linked to an existing player.
- [ ] An invite is a unique URL (`/register/<token>/`) that the admin shares personally.
- [ ] The invitee sets their own username and password, and is linked to the player.
- [ ] Tokens are single use, expire after a set time, and are unguessable. Invalid or expired links show a friendly message.
- [ ] Requesting a login is rate-limited or spam-protected.
