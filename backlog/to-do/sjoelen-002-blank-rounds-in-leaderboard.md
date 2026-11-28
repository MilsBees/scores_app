# Blank rounds give inconsistent Sjoelen leaderboard numbers

### Who

- Sjoelen players looking at the leaderboard

### What

- The new-game form lets you leave a round blank.
- A game with a blank round counts as `round_1 + round_3` (the blank round as 0) in the top/bottom scores lists and in the median. The leaderboard's **best** and **average** columns, however, add the rounds up in the database, where one blank round makes the whole game total empty, so that game is silently left out.
- Example: five games of 120 plus one game of 90 / blank / 90. The top-scores list shows 180, but the player's best score shows 120 and the average ignores that game.
- Found by shared-006. The test is `sjoelen/tests/test_score_rules.py::test_game_with_blank_round_counts_in_leaderboard_like_everywhere_else`, currently marked as an expected failure.

### Why

- Every page should agree on a game's total.

### Acceptance Criteria

- [ ] Decide which rule is right: (a) a blank round counts as 0 everywhere, or (b) all three rounds are required when saving a game (and then check whether existing games have blank rounds).
- [ ] The leaderboard's best, average and median, the top and bottom lists, and the statistics page all use the same total.
- [ ] The expected-failure marker on the test is removed and the test passes.
