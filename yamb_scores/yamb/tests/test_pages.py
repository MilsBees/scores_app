"""Every Yamb page loads, with realistic data present."""
from django.test import TestCase
from django.urls import reverse

from yamb.models import YambGame

from .factories import make_yamb_dataset


class YambPagesWithDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anna, cls.bram, cls.cleo = make_yamb_dataset()
        cls.yamb_game = YambGame.objects.first()
        cls.scoresheet = cls.yamb_game.yamb_scoresheets.first()

    def assert_page_ok(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return response

    def test_simple_pages(self):
        for name in [
            "index", "rules", "game_list", "new_game", "player_list", "new_player",
            "yamb_list", "new_yamb", "player_stats", "yamb_statistics", "yamb_dashboard",
        ]:
            with self.subTest(page=name):
                self.assert_page_ok(reverse(f"scores:{name}"))

    def test_pages_for_one_object(self):
        urls = [
            reverse("scores:edit_player", args=[self.anna.pk]),
            reverse("scores:delete_player", args=[self.anna.pk]),
            reverse("scores:yamb_detail", args=[self.yamb_game.pk]),
            reverse("scores:edit_yamb_scoresheet", args=[self.yamb_game.pk, self.scoresheet.pk]),
            reverse("scores:delete_yamb_scoresheet", args=[self.yamb_game.pk, self.scoresheet.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assert_page_ok(url)

    def test_leaderboard_every_sort_and_toggle(self):
        for sort in ["best", "avg", "games", "median", "not-a-sort"]:
            for direction in ["asc", "desc"]:
                for show_all in ["true", "false"]:
                    with self.subTest(sort=sort, dir=direction, show_all=show_all):
                        response = self.assert_page_ok(
                            reverse("scores:leaderboard") + f"?sort={sort}&dir={direction}&show_all={show_all}"
                        )
                        self.assertContains(response, "Anna")

    def test_player_stats_for_a_player(self):
        response = self.assert_page_ok(reverse("scores:player_stats") + f"?player={self.anna.pk}")
        self.assertContains(response, "Anna")

    def test_player_stats_unknown_player_is_404(self):
        response = self.client.get(reverse("scores:player_stats") + "?player=999999")
        self.assertEqual(response.status_code, 404)

    def test_new_game_prefilled_from_yamb_game(self):
        response = self.assert_page_ok(reverse("scores:new_game") + f"?yamb_game_id={self.yamb_game.pk}")
        self.assertContains(response, "656")

    def test_new_game_with_unknown_yamb_game_still_loads(self):
        self.assert_page_ok(reverse("scores:new_game") + "?yamb_game_id=999999")

    def test_statistics_and_dashboard_show_data(self):
        self.assertContains(self.assert_page_ok(reverse("scores:yamb_statistics")), "Anna")
        self.assertContains(self.assert_page_ok(reverse("scores:yamb_dashboard")), "Anna")


class YambPagesWithoutDataTests(TestCase):
    """Pages must also work on an empty database (new install)."""

    def test_stats_pages_empty(self):
        for name in ["leaderboard", "player_stats", "yamb_statistics", "yamb_dashboard", "game_list", "yamb_list"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"scores:{name}")).status_code, 200)
