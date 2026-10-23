# Wedding board

This app is a private, self-contained wedding task board. It uses the project's Django database and session middleware, adds no accounts or external services, and is not linked from the existing score pages. Its route prefix is `WEDDING_URL_PREFIX` in `wedding/urls.py`; change that value to move the entire board.

## Enable and deploy

The app is enabled in this checkout by one `INSTALLED_APPS` entry and one root URL include. On a different checkout, add `'wedding'` to `INSTALLED_APPS` and add `path('', include('wedding.urls')),` to the root URL configuration. The application URL module supplies the `/wedding/` prefix.

The deployed app must run over HTTPS. The wedding login sets the wedding session cookie specifically with `Secure`, `HttpOnly`, `SameSite=Lax`, and a 90-day maximum age; it does not alter global cookie settings or `SESSION_COOKIE_AGE`. Login failures are limited per IP using Django's configured cache, with temporary lockout after repeated failures.

1. Open the PythonAnywhere **Web** tab and edit the WSGI file for the app. Before the `get_wsgi_application()` call, set the passphrase hash as an environment variable:

   ```python
   import os
   os.environ['WEDDING_PASSPHRASE_HASH'] = 'paste-the-generated-hash-here'
   ```

   Alternatively, add `WEDDING_PASSPHRASE_HASH=...` to the untracked `yamb_scores/.env` file; this project already uses `python-decouple` to read that file. Never add the plain passphrase or its hash to tracked files.

2. Generate a hash locally or in a PythonAnywhere Bash console:

   ```bash
   cd ~/scores_app/yamb_scores
   python manage.py make_wedding_hash
   ```

   Enter the passphrase twice, then copy the printed Django hash to the WSGI environment (or `.env`). Only the hash is stored by the app.

3. Run the schema migration and seed once:

   ```bash
   cd ~/scores_app/yamb_scores
   python manage.py migrate
   python manage.py seed_wedding
   ```

   `seed_wedding` is idempotent and creates all 29 initial tasks only if no cards exist. The three board columns are created by the schema migration.

4. Collect static files and reload the web app:

   ```bash
   python manage.py collectstatic --noinput
   ```

   Then return to PythonAnywhere's **Web** tab and click **Reload**.

The board is available at `https://<your-domain>/wedding/`. To export a backup, run `python manage.py export_wedding > wedding-backup.json` from `yamb_scores/`. Store backups securely because they contain the board's private contents.

## Security and existing project settings

The board requires the `WEDDING_PASSPHRASE_HASH` setting and uses Django's password hashers, CSRF middleware, and session framework. Its JSON endpoints require the wedding session and state-changing browser requests use the CSRF token header. Responses include `X-Robots-Tag: noindex, nofollow`; no existing `robots.txt` was present to update.

The existing project settings define `SECRET_KEY` from configuration but fall back to the literal development key `django-insecure-dev-key-change-in-production`. This app does not change it. Ensure PythonAnywhere supplies a unique secret key through its existing `SECRET_KEY` environment/configuration before production use.

Existing global session-cookie settings are not modified. Django's defaults are HttpOnly and SameSite=Lax, while the default Secure flag is false; the wedding login applies all three attributes to its own session cookie only. The application cache must be available to all workers for rate limiting to be shared across workers.

## Tests

From `yamb_scores/`, run:

```bash
python manage.py test wedding
```
