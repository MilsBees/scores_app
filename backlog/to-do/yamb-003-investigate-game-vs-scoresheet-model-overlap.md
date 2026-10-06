# Investigate Yamb Game vs Scoresheet Model Overlap

### Who

<!--Who does this benefit or who will this affect? Who should be able to view this?-->

- Developers and maintainers of the Yamb app
- Admins using the Django admin interface

### What

<!--What problem needs addressing?-->

- In Django admin, Yamb currently shows separate entities for scoresheets, games, and scores
- It is unclear whether `YambGame` and `YambScoresheet` represent meaningfully different concepts or duplicate the same concept with different names
- This creates confusion in data modeling, admin usage, and future feature work

### Why

<!--What value does this add?-->

- Clarifies the domain model so future changes are safer and easier
- Reduces risk of double-entry or inconsistent records across overlapping models
- Makes admin and reporting behavior easier to reason about

### Acceptance Criteria

<!--Testable done conditions; avoid implementation detail.-->

- [ ] Document current responsibilities of `Game`, `Score`, `YambGame`, and `YambScoresheet`
- [ ] Map how each model is used in views, forms, templates, stats, and admin
- [ ] Confirm whether `YambGame` and `YambScoresheet` are truly distinct or effectively duplicates
- [ ] Propose one recommended direction: keep separate with clear boundaries, or merge/simplify
- [ ] List migration and backward-compatibility risks for the recommended direction
