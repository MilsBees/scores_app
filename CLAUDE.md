# Scores App

A small Django app for recording scores and statistics for games played by friends and family: **Yamb** (dice), **Squash**, and **Sjoelen** (Dutch shuffleboard), plus a private **wedding** task board. It runs on PythonAnywhere with SQLite and is in active daily use, so data safety comes first. Some users (the owner's parents) are not technical: the UI must stay simple, and they must never need Django admin.

The owner is not a developer. They can't review code line by line; they judge changes by using the app locally. So tests, CI and careful self-review carry the quality burden, and every PR needs a plain-language "How to check" list.

## Commands

Run everything from `yamb_scores/` (that's where `manage.py` lives). Use the venv at the repo root (`venv/`).

```powershell
cd yamb_scores
python manage.py runserver            # http://127.0.0.1:8000/
python manage.py test                 # full suite (what CI runs)
python manage.py test squash          # one app
python manage.py check
python manage.py makemigrations --check --dry-run   # CI fails if a migration is missing
```

Local config lives in `yamb_scores/.env` (untracked), and is read through `python-decouple`. Set `DEBUG=True` locally.

## Layout

- `yamb_scores/config/`: settings and root URLs
- `yamb_scores/{home,yamb,squash,sjoelen,wedding}/`: one Django app per game. Each owns its own models, forms, views, templates and tests.
- `yamb_scores/templates/`: the shared base template and includes
- `squash/views/` is mid-refactor: everything still lives in `__init__.py` (see `backlog/to-do/shared-001-*`). Target layout per app: `views/<concern>.py` modules re-exported from `views/__init__.py`, plus logic in `services/`.
- `backlog/`: the work items and roadmap. **Read `backlog/README.md` for how we work.**
- `docs/DEPLOY.md`: the PythonAnywhere deploy and rollback runbook

## Conventions

- **Thin views, logic in `services/`.** Calculations should be plain functions that can be unit tested.
- **Readable modules:** aim for at most about 200 lines per Python module. Don't hide a big module inside `__init__.py`.
- **Keep the apps independent.** The games share *patterns*, not *logic*. Share template includes and small utilities only. "Duplication is far cheaper than the wrong abstraction."
- Refactors preserve behaviour and URL names. Add the tests that prove it *before* moving code.
- Avoid N+1 queries on list and stats pages (`select_related` / `prefetch_related` / aggregation).

## Hard rules

- Never push to `main`. Use one branch and one PR per backlog item; the owner merges.
- Every behaviour change ships with tests. `python manage.py test` must pass before a PR.
- Migrations must be backward compatible and reversible. Data migrations need a reverse function, or an explicit note in the PR. Any PR with a migration says "back up the DB before deploying" in its deploy notes.
- Never touch production data or the production server. Deployment is done by the owner following `docs/DEPLOY.md`.
- Never commit `.env`, `db.sqlite3`, secrets or passphrase hashes.
- Security: every view that creates, edits or deletes data must require an authenticated user with permission (being introduced in `shared-004a`; after that it's mandatory). State-changing actions use POST with CSRF, never GET.
- Stay within the backlog item's scope. Write unrelated findings down as a new backlog item instead of fixing them on the side.
