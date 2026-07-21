from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from squash.models import SquashMatch, SquashPlayer, SquashSet
from squash.services.stats import get_leaderboard_stats


class LeaderboardStatsServiceTests(TestCase):
    def setUp(self):
        self.alice = SquashPlayer.objects.create(name="Alice")
        self.bob = SquashPlayer.objects.create(name="Bob")
        self.cara = SquashPlayer.objects.create(name="Cara")
        self.dan = SquashPlayer.objects.create(name="Dan")

        # Draw match (11-point)
        match_1 = SquashMatch.objects.create(
            player_1=self.alice,
            player_2=self.bob,
            date_played="2026-01-01",
            set_type="11",
        )
        SquashSet.objects.create(match=match_1, set_number=1, player_1_points=11, player_2_points=9)
        SquashSet.objects.create(match=match_1, set_number=2, player_1_points=9, player_2_points=11)

        # Alice wins match (21-point)
        match_2 = SquashMatch.objects.create(
            player_1=self.alice,
            player_2=self.cara,
            date_played="2026-01-02",
            set_type="21",
        )
        SquashSet.objects.create(match=match_2, set_number=1, player_1_points=21, player_2_points=18)
        SquashSet.objects.create(match=match_2, set_number=2, player_1_points=21, player_2_points=19)

        # Bob wins match (11-point)
        match_3 = SquashMatch.objects.create(
            player_1=self.bob,
            player_2=self.cara,
            date_played="2026-01-03",
            set_type="11",
        )
        SquashSet.objects.create(match=match_3, set_number=1, player_1_points=11, player_2_points=6)
        SquashSet.objects.create(match=match_3, set_number=2, player_1_points=11, player_2_points=7)

        # No-set match should not include Dan in leaderboard (total_sets == 0)
        SquashMatch.objects.create(
            player_1=self.dan,
            player_2=self.alice,
            date_played="2026-01-04",
            set_type="11",
        )

    def _by_name(self, stats):
        return {row["player"].name: row for row in stats}

    def test_get_leaderboard_stats_returns_relative_and_absolute_lists(self):
        relative_stats, absolute_stats = get_leaderboard_stats()

        self.assertIsInstance(relative_stats, list)
        self.assertIsInstance(absolute_stats, list)
        self.assertEqual(len(relative_stats), len(absolute_stats))

        by_name = self._by_name(relative_stats)
        self.assertSetEqual(set(by_name.keys()), {"Alice", "Bob", "Cara"})

        alice = by_name["Alice"]
        self.assertEqual(alice["points_for"], 62)
        self.assertEqual(alice["points_against"], 57)
        self.assertEqual(alice["point_diff"], 5)
        self.assertEqual(alice["total_sets"], 4)
        self.assertEqual(alice["total_sets_won"], 3)
        self.assertEqual(alice["total_sets_lost"], 1)
        self.assertEqual(alice["matches_won"], 1)
        self.assertEqual(alice["matches_drawn"], 2)
        self.assertEqual(alice["matches_lost"], 0)
        self.assertEqual(alice["matches_played"], 3)
        self.assertEqual(str(alice["last_match_date"]), "2026-01-04")
        self.assertAlmostEqual(alice["match_win_pct"], 33.3333, places=3)
        self.assertAlmostEqual(alice["set_win_pct"], 75.0, places=3)
        self.assertAlmostEqual(alice["point_win_pct"], 52.1008, places=3)

    def test_get_leaderboard_stats_respects_set_type_filter(self):
        relative_stats, _ = get_leaderboard_stats(set_type_filter="11")
        by_name = self._by_name(relative_stats)

        self.assertSetEqual(set(by_name.keys()), {"Alice", "Bob", "Cara"})

        alice = by_name["Alice"]
        self.assertEqual(alice["points_for"], 20)
        self.assertEqual(alice["points_against"], 20)
        self.assertEqual(alice["total_sets"], 2)
        self.assertEqual(alice["matches_won"], 0)
        self.assertEqual(alice["matches_drawn"], 2)
        self.assertEqual(alice["matches_lost"], 0)
        self.assertEqual(alice["matches_played"], 2)

    def test_get_leaderboard_stats_uses_low_query_count(self):
        with CaptureQueriesContext(connection) as queries:
            get_leaderboard_stats()

        self.assertLessEqual(len(queries), 15)
