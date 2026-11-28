"""Squash stats pages with realistic data, every sort and filter toggle."""
from django.test import TestCase
from django.urls import reverse

from squash.tests.factories import make_match, make_player, make_squash_dataset

SET_TYPES = ["", "11", "21", "bogus"]


class SquashPagesWithDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.milan, cls.guus, cls.cleo = make_squash_dataset()

    def assert_page_ok(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return response

    def test_match_list_and_players(self):
        self.assertContains(self.assert_page_ok(reverse("squash:match_list")), "Guus")
        self.assertContains(self.assert_page_ok(reverse("squash:player_list")), "Cleo")

    def test_leaderboard_every_sort_and_set_type(self):
        abs_sorts = ["matches_won", "matches_drawn", "matches_lost", "matches_played",
                     "points_for", "points_against", "point_diff", "last_match_date", "bogus"]
        rel_sorts = ["match_win_pct", "set_win_pct", "point_win_pct", "points_for",
                     "points_against", "matches_played", "total_sets", "bogus"]
        for set_type in SET_TYPES:
            for direction in ["asc", "desc"]:
                for abs_sort in abs_sorts:
                    with self.subTest(set_type=set_type, abs_sort=abs_sort, dir=direction):
                        response = self.assert_page_ok(
                            reverse("squash:leaderboard")
                            + f"?set_type={set_type}&abs_sort={abs_sort}&abs_dir={direction}"
                        )
                        self.assertContains(response, "Milan")
                for rel_sort in rel_sorts:
                    with self.subTest(set_type=set_type, rel_sort=rel_sort, dir=direction):
                        self.assert_page_ok(
                            reverse("squash:leaderboard")
                            + f"?set_type={set_type}&rel_sort={rel_sort}&rel_dir={direction}"
                        )

    def test_h2h_every_player_sort_and_set_type(self):
        sorts = ["points_for", "points_against", "point_diff", "sets_won", "sets_lost",
                 "matches_won", "matches_lost", "matches_drawn", "bogus"]
        for player in [self.milan, self.guus, self.cleo]:
            for set_type in SET_TYPES:
                for sort in sorts:
                    with self.subTest(player=player.name, set_type=set_type, sort=sort):
                        self.assert_page_ok(
                            reverse("squash:h2h") + f"?player={player.pk}&set_type={set_type}&sort={sort}&dir=asc"
                        )
        response = self.assert_page_ok(reverse("squash:h2h") + f"?player={self.milan.pk}")
        self.assertContains(response, "Guus")

    def test_h2h_unknown_player_is_404(self):
        self.assertEqual(self.client.get(reverse("squash:h2h") + "?player=999999").status_code, 404)

    def test_statistics_every_set_type_and_incomplete_toggle(self):
        for set_type in SET_TYPES:
            for include_incomplete in ["", "1"]:
                with self.subTest(set_type=set_type, include_incomplete=include_incomplete):
                    response = self.assert_page_ok(
                        reverse("squash:statistics") + f"?set_type={set_type}&include_incomplete={include_incomplete}"
                    )
                    self.assertContains(response, "Milan")



class SquashIncompleteToggleTests(TestCase):
    def test_statistics_incomplete_toggle_changes_match_extremes(self):
        # include_incomplete only affects the "match extremes" section.
        milan, guus = make_player("Milan"), make_player("Guus")
        make_match(milan, guus, [(11, 9), (9, 0)])  # 9-0 is incomplete (nobody reached 11)
        # Note: the page only counts incomplete sets when a set type is selected (see squash-003).
        url = reverse("squash:statistics") + "?set_type=11"

        without = self.client.get(url).context
        with_incomplete = self.client.get(url + "&include_incomplete=1").context

        self.assertEqual(without["incomplete_sets"], 1)
        single_set = lambda ctx: next(e for e in ctx["match_extremes"] if e["type"] == "Point differential (Single set)")
        self.assertEqual(single_set(without)["largest_display"], "Milan 11-9 Guus")
        self.assertEqual(single_set(with_incomplete)["largest_display"], "Milan 9-0 Guus")


class SquashPagesWithoutDataTests(TestCase):
    def test_stats_pages_empty(self):
        for name in ["leaderboard", "h2h", "statistics", "match_list", "player_list"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"squash:{name}")).status_code, 200)
