# Deploying to PythonAnywhere

The app runs on PythonAnywhere using SQLite (`yamb_scores/db.sqlite3` on the server). Deploying is manual and takes a few minutes. A reload causes only a few seconds of downtime.

The paths below assume the repo is checked out at `~/scores_app` on the server, which matches the wedding README. Adjust them if yours differs.

## Before you start

- The PR is merged into `main` on GitHub and CI is green.
- Read the PR's **Deploy notes**: is there a migration? new settings or env vars?

## Steps (in a PythonAnywhere Bash console)

```bash
cd ~/scores_app

# 1. Note the current commit, so you can go back to it
git rev-parse HEAD > ~/last_deployed_commit.txt

# 2. Back up the database (always; it's cheap)
mkdir -p ~/db_backups
cp yamb_scores/db.sqlite3 ~/db_backups/db-$(date +%Y%m%d-%H%M%S).sqlite3

# 3. Get the new code
git pull origin main

# 4. Update dependencies (activate your virtualenv first if you use one)
pip install -r requirements.txt

# 5. Apply migrations and static files
cd yamb_scores
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

6. Open the PythonAnywhere **Web** tab and click **Reload**.
7. Smoke-check the live site: the home page, then each game's leaderboard and statistics page, then any page the PR changed.

## Rollback

If something is wrong after a deploy:

```bash
cd ~/scores_app
git checkout $(cat ~/last_deployed_commit.txt)
```

- **If the deploy included a migration**, also restore the backup you made in step 2. Stop and think first: any scores entered *after* the deploy will be lost, so note them down to re-enter.
  ```bash
  cp ~/db_backups/<the-backup-file>.sqlite3 yamb_scores/db.sqlite3
  ```
- Reload in the **Web** tab and smoke-check the site again.
- Then fix forward on a new branch, and run `git checkout main` on the server before the next deploy.

## Production settings checklist

These are set in the WSGI file (`os.environ[...]`) or in `yamb_scores/.env` on the server. Never put them in git.

| Setting | Value in production |
|---|---|
| `DEBUG` | `False` (or leave it unset) |
| `SECRET_KEY` | a long random value, unique to the server |
| `ALLOWED_HOSTS` | your PythonAnywhere domain, for example `<user>.pythonanywhere.com` |
| `WEDDING_PASSPHRASE_HASH` | see `yamb_scores/wedding/README.md` |

`shared-007` will add more settings here (HTTPS and cookie security) and will make a missing `SECRET_KEY` an error.

To generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Backups

Keep a few recent files in `~/db_backups/` and occasionally download one to your own computer. You can delete old ones to save space.
