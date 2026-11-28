# Can't add more sets to a Squash session later the same day

### Who

- Squash players who enter a session in more than one go (for example, a few sets now and the rest after playing)

### What

- If a session already exists for a date, submitting the "New session" form again for that date fails with "Squash session with this Date played already exists". Nothing is saved.
- The view's code is clearly meant to handle this: it looks up the existing session and match and keeps numbering the sets. But the form's built-in check that dates are unique rejects the submission before that code runs.
- Found by shared-006. The test is `squash/tests/views/test_post_flows_db.py::test_second_session_entry_on_same_date_adds_to_existing_match`, currently marked as an expected failure.

### Why

- Without the fix, sets played later in the day either get lost or have to be entered one match at a time through "New match".

### Acceptance Criteria

- [ ] Confirm the intended behaviour: should a second entry on the same date add to the existing session (as the code intends), or show a clear message pointing to that session?
- [ ] With the intended behaviour in place, the expected-failure marker on the test is removed and the test passes.
- [ ] Sets added later continue the set numbering of the existing match (1, 2, then 3…).
