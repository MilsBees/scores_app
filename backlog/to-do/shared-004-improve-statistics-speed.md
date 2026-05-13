# Improve Statistics Page Performance

### Who

<!--Who does this benefit or who will this affect? Who should be able to view this?-->

- All users viewing statistics pages

### What

<!--What problem needs addressing?-->

- The statistics pages are slow to load due to heavy database queries and calculations performed on each request
- Changing filters or toggles (e.g., set type filter, include incomplete sets) causes a full page reload instead of updating just the affected elements
- This makes the user experience feel sluggish and unresponsive

### Why

<!--What value does this add?-->

- Faster page loads improve user experience
- Partial updates via AJAX make interactions feel more responsive
- Reduces server load by avoiding full page renders for small changes

### Acceptance Criteria

<!--Testable done conditions; avoid implementation detail.-->

- [ ] Filter toggles update charts without full page reload (using AJAX)
- [ ] Statistics page loads noticeably faster
- [ ] Consider caching expensive calculations or using database aggregations instead of Python loops
