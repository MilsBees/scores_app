"""Every Sjoelen create/edit/delete flow changes the database as expected."""
from django.test import TestCase
from django.urls import reverse

from sjoelen.models import SjoelenGame, SjoelenPlayer, SjoelenScore

from .factories import make_player


def game_data(rows):
    """rows: list of (player_pk_or_empty, r1, r2, r3)."""
    data = {
        "scores-TOTAL_FORMS": str(len(rows)),
        "scores-INITIAL_FORMS": "0",
        "scores-MIN_NUM_FORMS": "0",
        "scores-MAX_NUM_FORMS": "1000",
    }
    for i, (player, r1, r2, r3) in enumerate(rows):
        data.update({
            f"scores-{i}-player": player,
            f"scores-{i}-round_1": r1,
            f"scores-{i}-round_2": r2,
            f"scores-{i}-round_3": r3,
        })
    return data


class SjoelenGamePostTests(TestCase):
    def setUp(self):
        self.anna = make_player("Anna")
        self.bram = make_player("Bram")

    def test_new_game_saves_rounds(self):
        response = self.client.post(
            reverse("sjoelen:new_game"),
            game_data([(self.anna.pk, "40", "38", "45"), (self.bram.pk, "30", "35", "28")]),
        )

        self.assertRedirects(response, reverse("sjoelen:game_list"))
        game = SjoelenGame.objects.get()
        self.assertEqual(
            {(s.player.name, s.round_1, s.round_2, s.round_3, s.final_score) for s in game.scores.all()},
            {("Anna", 40, 38, 45, 123), ("Bram", 30, 35, 28, 93)},
        )

    def test_same_player_twice_is_rejected(self):
        response = self.client.post(
            reverse("sjoelen:new_game"),
            game_data([(self.anna.pk, "40", "38", "45"), (self.anna.pk, "30", "35", "28")]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SjoelenGame.objects.count(), 0)

    def test_scores_without_player_are_rejected(self):
        response = self.client.post(reverse("sjoelen:new_game"), game_data([("", "40", "38", "45")]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SjoelenScore.objects.count(), 0)


class SjoelenPlayerPostTests(TestCase):
    def test_new_player_is_saved_title_cased(self):
        response = self.client.post(reverse("sjoelen:new_player"), {"name": "dora"})

        self.assertRedirects(response, reverse("sjoelen:player_list"))
        self.assertTrue(SjoelenPlayer.objects.filter(name="Dora").exists())

    def test_duplicate_player_name_is_rejected_case_insensitive(self):
        make_player("Dora")
        response = self.client.post(reverse("sjoelen:new_player"), {"name": "DORA"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SjoelenPlayer.objects.count(), 1)

    def test_edit_player_renames(self):
        player = make_player("Cara")
        response = self.client.post(reverse("sjoelen:edit_player", args=[player.pk]), {"name": "Carla"})

        self.assertRedirects(response, reverse("sjoelen:player_list"))
        player.refresh_from_db()
        self.assertEqual(player.name, "Carla")

    def test_delete_player_removes_player(self):
        player = make_player("Cara")
        response = self.client.post(reverse("sjoelen:delete_player", args=[player.pk]))

        self.assertRedirects(response, reverse("sjoelen:player_list"))
        self.assertFalse(SjoelenPlayer.objects.filter(pk=player.pk).exists())

    def test_delete_page_get_does_not_delete(self):
        player = make_player("Cara")
        self.client.get(reverse("sjoelen:delete_player", args=[player.pk]))
        self.assertTrue(SjoelenPlayer.objects.filter(pk=player.pk).exists())
