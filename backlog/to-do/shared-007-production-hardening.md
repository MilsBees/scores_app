# Production settings hardening

### Who

- Everyone using the live site

### What

- `config/settings.py` falls back to a hard-coded, publicly visible `SECRET_KEY` if none is configured.
- No production security settings: session and CSRF cookies aren't marked Secure, and there's no HSTS or HTTPS redirect.
- `python manage.py check --deploy` reports warnings.

### Why

- A leaked or default secret key lets attackers forge sessions. That matters once logins exist (shared-004a).
- Secure cookies and HTTPS settings protect login sessions on public Wi-Fi.

### Acceptance Criteria

- [ ] With `DEBUG=False`, the app refuses to start without a real `SECRET_KEY`. Local development with `DEBUG=True` still works without one.
- [ ] Production enables secure session and CSRF cookies, HTTPS redirect, HSTS, and the proxy SSL header (PythonAnywhere terminates HTTPS), driven by settings or env vars so local HTTP development keeps working.
- [ ] `python manage.py check --deploy` has no warnings with production-like env vars (verified in a test or CI step).
- [ ] `docs/DEPLOY.md` lists every required production env var, plus the steps to set them on PythonAnywhere *before* deploying this change.

### Notes

- Deploy carefully: the server must have `SECRET_KEY` set before this ships, or the site won't start. Put that in the PR's deploy notes.
- Start HSTS with a short max-age, then raise it once confirmed.
