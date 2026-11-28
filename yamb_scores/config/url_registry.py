"""Every named URL in the project, sorted into read pages and write pages.

READ_URLS only show data. WRITE_URLS create, edit or delete data, and shared-004a
will require a login for all of them. `config/tests/test_url_registry.py` fails if
a URL is added without being listed here, so a new write page can't slip through
unprotected.

Names are "namespace:name". Django admin is left out: it has its own staff-only login.
"""

READ_URLS = {
    "home:home",
    # Yamb (namespace "scores")
    "scores:index",
    "scores:rules",
    "scores:game_list",
    "scores:leaderboard",
    "scores:player_stats",
    "scores:yamb_statistics",
    "scores:yamb_dashboard",
    "scores:player_list",
    "scores:yamb_list",
    "scores:yamb_detail",
    # Squash
    "squash:index",
    "squash:match_list",
    "squash:leaderboard",
    "squash:h2h",
    "squash:statistics",
    "squash:player_list",
    # Sjoelen
    "sjoelen:index",
    "sjoelen:game_list",
    "sjoelen:player_list",
    "sjoelen:leaderboard",
    "sjoelen:player_stats",
    "sjoelen:statistics",
}

WRITE_URLS = {
    # Yamb
    "scores:new_game",
    "scores:new_player",
    "scores:edit_player",
    "scores:delete_player",
    "scores:new_yamb",
    "scores:edit_yamb_scoresheet",
    "scores:delete_yamb_scoresheet",
    # Squash
    "squash:new_match",
    "squash:new_session",
    "squash:new_player",
    "squash:edit_player",
    "squash:delete_player",
    # Sjoelen
    "sjoelen:new_game",
    "sjoelen:new_player",
    "sjoelen:edit_player",
    "sjoelen:delete_player",
}

# The wedding board has its own passphrase login (see wedding/README.md) and
# isn't part of the scores login system.
SEPARATELY_PROTECTED_URLS = {
    "wedding:login",
    "wedding:logout",
    "wedding:board",
    "wedding:api_board",
    "wedding:api_cards",
    "wedding:api_card",
    "wedding:api_move_card",
}

IGNORED_NAMESPACES = {"admin"}
