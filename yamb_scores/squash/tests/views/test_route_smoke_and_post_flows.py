from django.test import TestCase
from django.urls import reverse

from squash.models import SquashPlayer


class SquashRouteSmokeTests(TestCase):
    def setUp(self):
        self.player = SquashPlayer.objects.create(name="Route Player")

    def test_all_squash_get_routes_are_reachable(self):
        routes = [
            reverse("squash:index"),
            reverse("squash:new_match"),
            reverse("squash:new_session"),
            reverse("squash:match_list"),
            reverse("squash:leaderboard"),
            reverse("squash:h2h"),
            reverse("squash:statistics"),
            reverse("squash:player_list"),
            reverse("squash:new_player"),
            reverse("squash:edit_player", kwargs={"pk": self.player.pk}),
            reverse("squash:delete_player", kwargs={"pk": self.player.pk}),
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)


class SquashPostFlowRedirectTests(TestCase):
    def setUp(self):
        self.player_1 = SquashPlayer.objects.create(name="Alice")
        self.player_2 = SquashPlayer.objects.create(name="Bob")
        self.player_3 = SquashPlayer.objects.create(name="Cara")

    def test_new_match_post_redirects_to_match_list(self):
        response = self.client.post(
            reverse("squash:new_match"),
            {
                "player_1": self.player_1.pk,
                "player_2": self.player_2.pk,
                "date_played": "2026-02-01",
                "set_type": "11",
                "sets-TOTAL_FORMS": "1",
                "sets-INITIAL_FORMS": "0",
                "sets-MIN_NUM_FORMS": "0",
                "sets-MAX_NUM_FORMS": "1000",
                "sets-0-player_1_points": "11",
                "sets-0-player_2_points": "9",
            },
        )

        self.assertRedirects(response, reverse("squash:match_list"))

    def test_new_session_post_redirects_to_match_list(self):
        response = self.client.post(
            reverse("squash:new_session"),
            {
                "date_played": "2026-02-02",
                "set_type": "11",
                "sets-TOTAL_FORMS": "1",
                "sets-INITIAL_FORMS": "0",
                "sets-MIN_NUM_FORMS": "0",
                "sets-MAX_NUM_FORMS": "1000",
                "sets-0-player_a": self.player_1.pk,
                "sets-0-player_b": self.player_2.pk,
                "sets-0-player_a_points": "11",
                "sets-0-player_b_points": "7",
            },
        )

        self.assertRedirects(response, reverse("squash:match_list"))

    def test_new_player_post_redirects_to_player_list(self):
        response = self.client.post(
            reverse("squash:new_player"),
            {
                "name": "Dora",
            },
        )

        self.assertRedirects(response, reverse("squash:player_list"))

    def test_edit_player_post_redirects_to_player_list(self):
        response = self.client.post(
            reverse("squash:edit_player", kwargs={"pk": self.player_3.pk}),
            {
                "name": "Cara Updated",
            },
        )

        self.assertRedirects(response, reverse("squash:player_list"))

    def test_delete_player_post_redirects_to_player_list(self):
        response = self.client.post(
            reverse("squash:delete_player", kwargs={"pk": self.player_3.pk}),
            {},
        )

        self.assertRedirects(response, reverse("squash:player_list"))
