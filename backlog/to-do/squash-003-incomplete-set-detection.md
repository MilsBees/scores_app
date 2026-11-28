# Fix incomplete-set detection for Squash

### Who

- Squash players looking at statistics, and the owner correcting data in admin

### What

- A set that finished 22-22 (Milan vs Guus, 9 August, set 2) is stored as *complete*, and can't be changed to incomplete in Django admin.
- Cause: `SquashSet.save()` (`squash/models.py`) recalculates `is_incomplete` on **every** save, using only "did anyone reach 11/21?". That has two effects:
  - Ticking "is incomplete" in admin is silently overwritten when you save, even though the checkbox is shown as editable.
  - Ties, and sets without a 2-point lead (22-22, 21-20, 11-11), count as complete even though nobody won them. A tie has no winner at all (`winner` returns `None`), so it can distort the win, set and point stats.

### Why

- Wrong "complete" flags make the statistics wrong, especially with the `include_incomplete` toggle.
- Admin must not show a field that ignores what you enter.

### Acceptance Criteria

- [ ] A set is automatically marked incomplete when it's a tie, or when nobody reached the target (11/21) with a lead of at least 2 points.
- [ ] It's possible to mark a set as incomplete by hand (for example, the set was stopped), and that choice survives saving, both in admin and wherever sets are edited.
- [ ] Existing sets in the database are re-checked with the new rule by a reversible data migration. The PR lists how many sets change, so the owner can sanity-check the number. The 9 August 22-22 set becomes incomplete.
- [ ] Tests cover: 11-9 complete, 12-10 complete, 11-10 incomplete, 11-11 incomplete, 22-22 incomplete (21-point), 8-5 incomplete, a manual override that survives a save, and a check that nothing changes via admin unless you change it.

### Notes

- To confirm at the planning step: does "win by 2" match your house rules for both set types? Should a manual "incomplete" tick only ever *add* incompleteness, or also be able to mark an auto-detected incomplete set as complete?
- Has a migration, so back up the DB before deploying.
