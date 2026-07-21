from django.test import TestCase
from django.urls import reverse

from squash.models import SquashMatch, SquashPlayer, SquashSet


class LeaderboardViewSortingTests(TestCase):
    def setUp(self):
        self.player_a = SquashPlayer.objects.create(name="Anna")
        self.player_b = SquashPlayer.objects.create(name="Bram")
        self.player_c = SquashPlayer.objects.create(name="Cleo")

        match_1 = SquashMatch.objects.create(
            player_1=self.player_a,
            player_2=self.player_b,
            date_played="2026-01-01",
            set_type="11",
        )
        SquashSet.objects.create(match=match_1, set_number=1, player_1_points=11, player_2_points=9)

        match_2 = SquashMatch.objects.create(
            player_1=self.player_b,
            player_2=self.player_c,
            date_played="2026-01-02",
            set_type="11",
        )
        SquashSet.objects.create(match=match_2, set_number=1, player_1_points=11, player_2_points=8)

    def test_last_match_sort_desc_orders_newest_first(self):
        response = self.client.get(
            reverse("squash:leaderboard"),
            {"abs_sort": "last_match_date", "abs_dir": "desc"},
        )

        self.assertEqual(response.status_code, 200)
        dates = [row["last_match_date"] for row in response.context["absolute_stats"]]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_last_match_sort_asc_orders_oldest_first(self):
        response = self.client.get(
            reverse("squash:leaderboard"),
            {"abs_sort": "last_match_date", "abs_dir": "asc"},
        )

        self.assertEqual(response.status_code, 200)
        dates = [row["last_match_date"] for row in response.context["absolute_stats"]]
        self.assertEqual(dates, sorted(dates))
