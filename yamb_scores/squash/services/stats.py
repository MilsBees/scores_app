from __future__ import annotations

from typing import Any

from ..models import SquashMatch


def get_leaderboard_stats(set_type_filter: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build leaderboard stats with a query-efficient match/sets preload."""
    if set_type_filter not in ("11", "21"):
        set_type_filter = None

    matches = SquashMatch.objects.select_related("player_1", "player_2").prefetch_related("sets")
    if set_type_filter:
        matches = matches.filter(set_type=set_type_filter)

    stats_by_player: dict[int, dict[str, Any]] = {}

    def _ensure_player_stats(player) -> dict[str, Any]:
        if player.id not in stats_by_player:
            stats_by_player[player.id] = {
                "player": player,
                "points_for": 0,
                "points_against": 0,
                "total_sets_won": 0,
                "total_sets_lost": 0,
                "total_sets": 0,
                "last_match_date": None,
                "matches_won": 0,
                "matches_lost": 0,
                "matches_drawn": 0,
            }
        return stats_by_player[player.id]

    for match in matches:
        p1_stats = _ensure_player_stats(match.player_1)
        p2_stats = _ensure_player_stats(match.player_2)

        last_date = match.date_played
        if p1_stats["last_match_date"] is None or last_date > p1_stats["last_match_date"]:
            p1_stats["last_match_date"] = last_date
        if p2_stats["last_match_date"] is None or last_date > p2_stats["last_match_date"]:
            p2_stats["last_match_date"] = last_date

        p1_sets_won_in_match = 0
        p2_sets_won_in_match = 0

        for set_obj in match.sets.all():
            p1_points = set_obj.player_1_points
            p2_points = set_obj.player_2_points

            p1_stats["points_for"] += p1_points
            p1_stats["points_against"] += p2_points
            p2_stats["points_for"] += p2_points
            p2_stats["points_against"] += p1_points

            p1_stats["total_sets"] += 1
            p2_stats["total_sets"] += 1

            if p1_points > p2_points:
                p1_sets_won_in_match += 1
                p1_stats["total_sets_won"] += 1
                p2_stats["total_sets_lost"] += 1
            elif p2_points > p1_points:
                p2_sets_won_in_match += 1
                p2_stats["total_sets_won"] += 1
                p1_stats["total_sets_lost"] += 1

        if p1_sets_won_in_match > p2_sets_won_in_match:
            p1_stats["matches_won"] += 1
            p2_stats["matches_lost"] += 1
        elif p2_sets_won_in_match > p1_sets_won_in_match:
            p2_stats["matches_won"] += 1
            p1_stats["matches_lost"] += 1
        else:
            p1_stats["matches_drawn"] += 1
            p2_stats["matches_drawn"] += 1

    player_stats: list[dict[str, Any]] = []
    for stat in stats_by_player.values():
        if stat["total_sets"] <= 0:
            continue

        points_for = stat["points_for"]
        points_against = stat["points_against"]
        points_total = points_for + points_against

        matches_played = stat["matches_won"] + stat["matches_lost"] + stat["matches_drawn"]

        stat["points_total"] = points_total
        stat["point_diff"] = points_for - points_against
        stat["point_win_pct"] = (points_for / points_total * 100.0) if points_total > 0 else 0.0
        stat["set_win_pct"] = (
            stat["total_sets_won"] / stat["total_sets"] * 100.0 if stat["total_sets"] > 0 else 0.0
        )
        stat["matches_played"] = matches_played
        stat["match_win_pct"] = (stat["matches_won"] / matches_played * 100.0) if matches_played > 0 else 0.0

        player_stats.append(stat)

    relative_stats = list(player_stats)
    absolute_stats = list(player_stats)
    return relative_stats, absolute_stats
