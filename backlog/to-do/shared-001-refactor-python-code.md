# Refactor Python Code for Maintainability

### Who

<!--Who does this benefit or who will this affect? Who should be able to view this?-->

- Developers maintaining the codebase

### What

<!--What problem needs addressing?-->

- The `views.py` files have grown large and contain many responsibilities (e.g., squash/views.py is 900+ lines)
- Complex calculations are mixed with view logic, making code harder to understand and test
- Similar patterns are repeated across different apps (squash, sjoelen, yamb)

### Why

<!--What value does this add?-->

- Smaller, focused files are easier to navigate and understand
- Separating business logic from views enables unit testing
- Following Django best practices improves maintainability

### Acceptance Criteria

<!--Testable done conditions; avoid implementation detail.-->

- [ ] Split large views.py files into logical modules (e.g., `views/statistics.py`, `views/crud.py`)
- [ ] Extract complex calculations into service functions or model methods
- [ ] Consider using Django class-based views where appropriate
- [ ] Remove code duplication across apps where possible

---

## Implementation Guidance

### Abstraction Philosophy

> "Duplication is far cheaper than the wrong abstraction"

**Keep apps independent** — each app (squash, sjoelen, yamb) owns its own models, views, and services. The games are fundamentally different:
- **Squash**: matches → sets → points, two players, win/loss
- **Sjoelen**: games → scores → rounds, multiple players, high score wins  
- **Yamb**: scoresheets → categories, single player, complex scoring rules

**Don't over-abstract** — they share *patterns*, not *logic*. Forcing them into generic abstractions would add complexity without benefit.

**What to share:**
| Share | Don't Share |
|-------|-------------|
| Utility functions | Business logic |
| Template components | Models |
| CSS/JS patterns | View implementations |

**Optional shared utilities:**
```
yamb_scores/
├── shared/                        # Shared utilities (optional)
│   ├── templatetags/
│   │   └── ui_tags.py            # {% set_type_toggle %}, {% sort_link %}
│   └── utils.py                   # date_range(), build_query_string()
```

---

## Target Structure (per app)

Each app should follow this pattern:

```
<app>/
├── views/
│   ├── __init__.py           # Re-exports all views for urls.py compatibility
│   ├── games.py              # index, game_list, new_game (or matches.py for squash)
│   ├── players.py            # player_list, new_player, edit_player, delete_player
│   ├── statistics.py         # statistics view
│   ├── leaderboard.py        # leaderboard view
│   └── <other>.py            # h2h.py (squash), player_stats.py (sjoelen), etc.
├── services/
│   ├── __init__.py
│   └── stats.py              # Reusable calculations (player stats, extremes, etc.)
├── models.py                 # (unchanged)
├── forms.py                  # (unchanged)
└── urls.py                   # (unchanged - imports from views/)
```

**Key principles:**
1. Views become thin — just handle request/response, call services
2. Services contain business logic — reusable, testable calculations
3. One concern per file — statistics.py only does statistics
4. `views/__init__.py` re-exports everything so urls.py doesn't change

---

## Sjoelen Refactor Plan (template for others)

Current: 1 file, ~390 lines, 10 functions

| Function | Target File | Notes |
|----------|-------------|-------|
| `index`, `game_list`, `new_game` | `views/games.py` | ~60 lines |
| `player_list`, `new_player`, `edit_player`, `delete_player` | `views/players.py` | ~50 lines |
| `statistics` | `views/statistics.py` | ~60 lines (uses services) |
| `leaderboard` | `views/leaderboard.py` | ~50 lines (uses services) |
| `player_stats` | `views/player_stats.py` | ~40 lines |

**Services to extract (`services/stats.py`):**
- `get_player_stats(player)` — avg, best, worst, median, std_dev, games_played
- `get_score_distribution(scores, bucket_size=10)` — histogram data
- `get_round_extremes()` — highest/lowest for each round
- `get_all_players_with_stats(min_games=0)` — annotated player list

---

## Squash Refactor Plan

Current: 1 file, ~900 lines, 11 functions

| Function | Target File | Notes |
|----------|-------------|-------|
| `index`, `match_list`, `new_match`, `new_session` | `views/matches.py` | ~130 lines |
| `player_list`, `new_player`, `edit_player`, `delete_player` | `views/players.py` | ~50 lines |
| `statistics` | `views/statistics.py` | ~100 lines (uses services) |
| `leaderboard` | `views/leaderboard.py` | ~80 lines (uses services) |
| `h2h` | `views/h2h.py` | ~80 lines |

**Services to extract (`services/stats.py`):**
- `get_player_performance(player, set_type_filter=None)` — match/set/point win %
- `get_match_extremes(matches, sets, include_incomplete=False)` — differentials
- `get_player_box_data(player, set_type_filter=None)` — scores for box plots
- `filter_by_set_type(queryset, set_type_filter)` — common filtering

---

## Yamb Refactor Plan

Current: 1 file, ~550 lines, 16 functions

**Note:** Yamb has two game systems:
- **Simple**: `Game` + `Score` — basic game with scores per player
- **Complex**: `YambGame` + `YambScoresheet` — full yamb scoresheet tracking

| Function | Target File | Notes |
|----------|-------------|-------|
| `index`, `game_list`, `new_game` | `views/games.py` | Simple game CRUD (~70 lines) |
| `yamb_list`, `new_yamb`, `yamb_detail`, `edit_yamb_scoresheet`, `delete_yamb_scoresheet` | `views/yamb_games.py` | Complex yamb CRUD (~100 lines) |
| `player_list`, `new_player`, `edit_player`, `delete_player` | `views/players.py` | ~50 lines |
| `player_stats` | `views/player_stats.py` | ~50 lines |
| `leaderboard` | `views/leaderboard.py` | ~70 lines (uses services) |
| `yamb_statistics` | `views/statistics.py` | ~80 lines (uses services) |
| `yamb_dashboard` | `views/dashboard.py` | ~60 lines (uses services) |

**Services to extract (`services/stats.py`):**
- `get_player_stats(player)` — avg, best, worst, median, games_played
- `get_score_distribution(scores, bucket_size=10)` — histogram data
- `get_row_extremes()` — highest/lowest per yamb row (reusable for statistics)
- `get_all_players_with_stats(min_games=0)` — annotated player list
- `get_player_consistency(min_games=2)` — std dev for consistency ranking
