"""Every Sjoelen page loads, with realistic data present."""
from django.test import TestCase
from django.urls import reverse

from .factories import make_sjoelen_dataset


class SjoelenPagesWithDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anna, cls.bram, cls.cleo = make_sjoelen_dataset()

    def assert_page_ok(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return response

    def test_simple_pages(self):
        for name in ["index", "new_game", "game_list", "player_list", "new_player", "player_stats", "statistics"]:
            with self.subTest(page=name):
                self.assert_page_ok(reverse(f"sjoelen:{name}"))

    def test_player_pages(self):
        for name in ["edit_player", "delete_player"]:
            with self.subTest(page=name):
                self.assert_page_ok(reverse(f"sjoelen:{name}", args=[self.anna.pk]))

    def test_leaderboard_every_sort_and_toggle(self):
        for sort in ["best", "avg", "games", "median", "not-a-sort"]:
            for direction in ["asc", "desc"]:
                for show_all in ["true", "false"]:
                    with self.subTest(sort=sort, dir=direction, show_all=show_all):
                        response = self.assert_page_ok(
                            reverse("sjoelen:leaderboard") + f"?sort={sort}&dir={direction}&show_all={show_all}"
                        )
                        self.assertContains(response, "Anna")

    def test_player_stats_for_a_player(self):
        self.assertContains(self.assert_page_ok(reverse("sjoelen:player_stats") + f"?player={self.anna.pk}"), "Anna")

    def test_player_stats_unknown_player_is_404(self):
        self.assertEqual(self.client.get(reverse("sjoelen:player_stats") + "?player=999999").status_code, 404)

    def test_statistics_shows_data(self):
        self.assertContains(self.assert_page_ok(reverse("sjoelen:statistics")), "Anna")


class SjoelenPagesWithoutDataTests(TestCase):
    def test_stats_pages_empty(self):
        for name in ["leaderboard", "player_stats", "statistics", "game_list"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"sjoelen:{name}")).status_code, 200)
