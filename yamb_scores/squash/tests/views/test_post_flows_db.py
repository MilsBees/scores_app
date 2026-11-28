"""Squash create/edit/delete flows store exactly what was entered.

(The redirect-only checks live in test_route_smoke_and_post_flows.py.)
"""
from unittest import expectedFailure

from django.test import TestCase
from django.urls import reverse

from squash.models import SquashMatch, SquashPlayer, SquashSession, SquashSet
from squash.tests.factories import make_player


def management_form(total):
    return {
        "sets-TOTAL_FORMS": str(total),
        "sets-INITIAL_FORMS": "0",
        "sets-MIN_NUM_FORMS": "0",
        "sets-MAX_NUM_FORMS": "1000",
    }


class SquashMatchPostTests(TestCase):
    def setUp(self):
        self.milan = make_player("Milan")
        self.guus = make_player("Guus")

    def post_match(self, sets, set_type="11", **extra):
        data = {
            "player_1": self.milan.pk,
            "player_2": self.guus.pk,
            "date_played": "2026-08-09",
            "set_type": set_type,
            **management_form(len(sets)),
            **extra,
        }
        for i, (p1, p2) in enumerate(sets):
            data[f"sets-{i}-player_1_points"] = p1
            data[f"sets-{i}-player_2_points"] = p2
        return self.client.post(reverse("squash:new_match"), data)

    def test_new_match_saves_sets_in_order(self):
        response = self.post_match([("21", "17"), ("15", "21"), ("21", "10")], set_type="21")

        self.assertRedirects(response, reverse("squash:match_list"))
        match = SquashMatch.objects.get()
        self.assertEqual(match.set_type, "21")
        self.assertEqual(str(match.date_played), "2026-08-09")
        self.assertEqual(
            list(match.sets.values_list("set_number", "player_1_points", "player_2_points")),
            [(1, 21, 17), (2, 15, 21), (3, 21, 10)],
        )

    def test_same_player_twice_is_rejected(self):
        response = self.post_match([("11", "5")], player_2=self.milan.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SquashMatch.objects.count(), 0)

    def test_negative_points_are_rejected(self):
        response = self.post_match([("11", "-1")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SquashMatch.objects.count(), 0)


class SquashSessionPostTests(TestCase):
    def setUp(self):
        self.milan = make_player("Milan")
        self.guus = make_player("Guus")
        self.cleo = make_player("Cleo")

    def post_session(self, rows, set_type="11", date_played="2026-08-09"):
        data = {"date_played": date_played, "set_type": set_type, **management_form(len(rows))}
        for i, (a, b, a_points, b_points) in enumerate(rows):
            data.update({
                f"sets-{i}-player_a": a.pk,
                f"sets-{i}-player_b": b.pk,
                f"sets-{i}-player_a_points": a_points,
                f"sets-{i}-player_b_points": b_points,
            })
        return self.client.post(reverse("squash:new_session"), data)

    def test_sets_for_the_same_pair_become_one_match(self):
        # Guus is entered as player A in the second row; the points must follow the player.
        response = self.post_session([
            (self.milan, self.guus, "11", "7"),
            (self.guus, self.milan, "11", "9"),
            (self.guus, self.cleo, "8", "11"),
        ])

        self.assertRedirects(response, reverse("squash:match_list"))
        session = SquashSession.objects.get()
        self.assertEqual(session.matches.count(), 2)
        match = session.matches.get(player_1=self.milan, player_2=self.guus)
        self.assertEqual(
            list(match.sets.values_list("set_number", "player_1_points", "player_2_points")),
            [(1, 11, 7), (2, 9, 11)],
        )

    @expectedFailure  # Known bug: squash-004. Remove this marker when it's fixed.
    def test_second_session_on_same_date_is_a_separate_session(self):
        # A morning and an afternoon session on the same day are two sessions.
        # Today the date must be unique, so the second one is rejected:
        # "Squash session with this Date played already exists."
        self.post_session([(self.milan, self.guus, "11", "7")])
        response = self.post_session([(self.milan, self.guus, "5", "11")])

        self.assertRedirects(response, reverse("squash:match_list"))
        self.assertEqual(SquashSession.objects.filter(date_played="2026-08-09").count(), 2)
        self.assertEqual(SquashMatch.objects.count(), 2)
        for match in SquashMatch.objects.all():
            with self.subTest(match=match.pk):
                self.assertEqual(list(match.sets.values_list("set_number", flat=True)), [1])

    def test_session_set_type_is_stored_on_match(self):
        self.post_session([(self.milan, self.guus, "21", "15")], set_type="21")
        self.assertEqual(SquashMatch.objects.get().set_type, "21")

    def test_same_player_on_both_sides_is_rejected(self):
        response = self.post_session([(self.milan, self.milan, "11", "7")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SquashSet.objects.count(), 0)


class SquashPlayerPostTests(TestCase):
    def test_new_player_is_saved(self):
        self.client.post(reverse("squash:new_player"), {"name": "dora"})
        self.assertTrue(SquashPlayer.objects.filter(name__iexact="dora").exists())

    def test_duplicate_player_name_is_rejected_case_insensitive(self):
        make_player("Dora")
        response = self.client.post(reverse("squash:new_player"), {"name": "DORA"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SquashPlayer.objects.count(), 1)

    def test_edit_player_renames(self):
        player = make_player("Cara")
        self.client.post(reverse("squash:edit_player", args=[player.pk]), {"name": "Carla"})
        player.refresh_from_db()
        self.assertEqual(player.name, "Carla")

    def test_delete_player_removes_player(self):
        player = make_player("Cara")
        self.client.post(reverse("squash:delete_player", args=[player.pk]))
        self.assertFalse(SquashPlayer.objects.filter(pk=player.pk).exists())

    def test_delete_page_get_does_not_delete(self):
        player = make_player("Cara")
        self.client.get(reverse("squash:delete_player", args=[player.pk]))
        self.assertTrue(SquashPlayer.objects.filter(pk=player.pk).exists())
