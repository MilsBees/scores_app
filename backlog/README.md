# How we work

This replaces the earlier multi-agent process (12 mandatory hand-offs, synced roadmap and slice files, copy-and-paste prompts). That process lives in git history if it's ever needed. Trust now comes from **automated tests, CI, and focused review**, with the owner approving at two points per item.

## Where things live

| What | Where |
|---|---|
| Goals, priorities, and the order of work | [`ROADMAP.md`](ROADMAP.md) |
| Work items | `to-do/` and `done/` |
| Project facts, commands, rules for Claude | [`../CLAUDE.md`](../CLAUDE.md) |
| Deploying to PythonAnywhere | [`../docs/DEPLOY.md`](../docs/DEPLOY.md) |

The current state is always: `ROADMAP.md` + open PRs on GitHub + `git log`. No session hand-off files.

## The flow for each item

1. **Pick:** the owner says "work on X" or "what's next?" (take the top of **Now** in the roadmap).
2. **Plan (owner gate 1):** Claude reads the item and the code and proposes a short plan covering scope, approach, tests, and migration/rollback notes if data changes. The owner approves or adjusts it. Big items get split into smaller, separately shippable PRs at this point.
3. **Build** on a branch named `<item-id>-<short-slug>` (for example `shared-006-test-safety-net`). Write or extend the tests first for any behaviour that's touched, then run the full suite.
4. **Review (automated):**
   - `/code-review` on the diff, and fix the real findings.
   - `/security-review` as well for anything touching auth, permissions, forms, or migrations.
   - Large or risky changes also get an independent review from a fresh subagent that has no prior context.
5. **PR** to `main`, containing:
   - **Summary** in plain language: what changes for users.
   - **Tests:** what was added, and the result of the full run.
   - **How to check:** the exact local URLs and clicks, and what you should see.
   - **Deploy notes:** migration? back up the DB first? new settings or env vars?
   - In the same PR: the item file moves to `done/` (with its checkboxes ticked) and `ROADMAP.md` is updated.
6. **Accept (owner gate 2):** CI is green, the owner runs the app locally and works through "How to check", then merges or asks for fixes in the PR or chat.
7. **Deploy** whenever convenient, following `docs/DEPLOY.md`.

New ideas or out-of-scope findings become new item files in `to-do/` and get a place in the roadmap. They don't get done on the side.

## Item files

Name: `<app>-NNN-short-slug.md`, where `<app>` is `shared`, `yamb`, `squash`, `sjoelen` or `wedding`. Sub-items of a big item get a letter (`shared-004a-…`).

Template:

```markdown
# <Title>

### Who
- Who benefits / is affected?

### What
- What problem needs addressing?

### Why
- What value does this add?

### Acceptance Criteria
- [ ] Testable done conditions; avoid implementation detail.

### Notes
<!-- Optional: design decisions, dependencies, remaining phases. Keep it short. -->
```
