# Login System & Unified Player Model

### Who

<!--Who does this benefit or who will this affect? Who should be able to view this?-->

- All app users (restricts access to registered users only)
- Admins managing player accounts and permissions

### What

<!--What problem needs addressing?-->

- App is currently accessible to anyone
- Player models are duplicated across Yamb, Squash, and Sjoelen apps
- No way for users to manage their own game records

### Why

<!--What value does this add?-->

- Restricts just anyone from editing or deleting games
- Unified player management simplifies maintenance
- Users can edit/delete games they participated in
- Anonymous users can just view things

### Acceptance Criteria

<!--Testable done conditions; avoid implementation detail.-->

- [ ] Anonymous users can view leaderboards, statistics, and game history but cannot edit anything
- [ ] Registered users can view all data and record new games/matches
- [ ] Registered users can edit/delete games their linked player participated in
- [ ] Only admins can edit/delete any game or manage players
- [ ] Players do not need an account to participate in a game, though this will need to be recorded by someone with an account
- [ ] A user can request a login on the home page
- [ ] Users can register via unique invite URL and set username + password
- [ ] Invite tokens expire after use

### Technical Details

#### Player Model
```
Player (accounts app)
├── name (required)
└── user (optional FK to User, null=True)
```
- **Linked Player**: Has a User account, can log in, edit games they participated in
- **Guest Player**: Just a name in the system, no account (for casual/one-time players). Must be recorded by a registered user.

#### Access Control
| Action | Anonymous | Registered User | Admin |
|--------|-----------|-----------------|-------|
| View leaderboards, statistics, game history | ✅ | ✅ | ✅ |
| Record new games/matches (can include guest players) | ❌ | ✅ | ✅ |
| Edit/Delete games their linked player participated in | ❌ | ✅ | ✅ |
| Edit/Delete any game | ❌ | ❌ | ✅ |
| Create guest players (when recording games) | ❌ | ✅ | ✅ |
| Edit/Delete players | ❌ | ❌ | ✅ |
| Request login | ✅ | ❌ | ❌ |

#### Registration: Invite Link System
1. User requests a login via button on the home page
2. Admin reviews request and generates an invite token (via admin panel)
3. System creates unique registration URL (`/register/<token>/`)
4. Admin shares link with invitee
5. Invitee clicks link, sets their own username + password
6. Token expires after use

#### Implementation Tasks
- [ ] Create `accounts` app with unified `Player` model (optional `user` FK)
- [ ] Write data migration to merge existing players by name (case-insensitive)
- [ ] Update `yamb`, `squash`, `sjoelen` models to use `accounts.Player`
- [ ] Update all views/forms/templates to reference unified Player
- [ ] Implement login/logout pages using Django's built-in auth
- [ ] Add "Request login" button on home page for anonymous users
- [ ] Create invite token model and admin action to generate invites
- [ ] Build registration view for invite links
- [ ] Add "participated in" check for edit/delete permissions (linked players only)
- [ ] Remove old player models after successful migration
