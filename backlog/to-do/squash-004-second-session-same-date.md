# Allow more than one Squash session on the same day

### Who

- Squash players who play twice in a day (for example, a morning and an afternoon session)

### What

- Only one session per date is possible. Submitting "New session" for a date that already has a session fails with "Squash session with this Date played already exists", and nothing is saved.
- Cause: `SquashSession.date_played` is `unique=True` in the database (`squash/models.py`), and the view looks up the session by date (`get_or_create(date_played=...)`), so a second session that day can't exist.
- Found by shared-006. The test is `squash/tests/views/test_post_flows_db.py::test_second_session_on_same_date_is_a_separate_session`, currently marked as an expected failure.

### Why

- A morning and an afternoon session are two separate sessions. Today the second one can't be entered at all, or would get mixed into the first.

### Acceptance Criteria

- [ ] Several sessions can exist on the same date. Each "New session" submission creates its own session, with its own matches and set numbering starting at 1.
- [ ] Existing sessions and their matches are unchanged. A migration removes the unique-date rule and is reversible as long as no date has more than one session.
- [ ] Wherever sessions are shown or chosen (the match list, the admin session dropdown), two sessions on the same date can be told apart, for example by their creation time.
- [ ] The expected-failure marker on the test is removed and the test passes.

### Notes

- Has a migration, so back up the DB before deploying.
- Check that the stats and H2H pages don't group by session date anywhere in a way that would merge the two sessions.
