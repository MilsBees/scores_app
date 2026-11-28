"""Every Yamb create/edit/delete flow changes the database as expected."""
from django.test import TestCase
from django.urls import reverse

from yamb.models import Game, Player, Score, YambGame, YambScoresheet

from .factories import COMPLETE_SHEET, COMPLETE_SHEET_FINAL_SCORE, make_player, make_yamb_game


def management_form(prefix, total, initial=0):
    return {
        f"{prefix}-TOTAL_FORMS": str(total),
        f"{prefix}-INITIAL_FORMS": str(initial),
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }


class YambSimpleGamePostTests(TestCase):
    def setUp(self):
        self.anna = make_player("Anna")
        self.bram = make_player("Bram")

    def test_new_game_saves_scores(self):
        data = {
            **management_form("scores", 2),
            "scores-0-player": self.anna.pk, "scores-0-score": "612",
            "scores-1-player": self.bram.pk, "scores-1-score": "-40",
        }
        response = self.client.post(reverse("scores:new_game"), data)

        self.assertRedirects(response, reverse("scores:game_list"))
        game = Game.objects.get()
        self.assertEqual(
            {(s.player.name, s.score) for s in game.scores.all()},
            {("Anna", 612), ("Bram", -40)},
        )

    def test_new_game_score_without_player_is_rejected(self):
        data = {**management_form("scores", 1), "scores-0-player": "", "scores-0-score": "500"}
        response = self.client.post(reverse("scores:new_game"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 0)
        self.assertEqual(Score.objects.count(), 0)


class YambScoresheetPostTests(TestCase):
    def setUp(self):
        self.anna = make_player("Anna")
        self.bram = make_player("Bram")

    def sheet_data(self, prefix, index, player, sheet):
        return {f"{prefix}-{index}-player": player.pk, **{f"{prefix}-{index}-{k}": v for k, v in sheet.items()}}

    def test_new_yamb_saves_scoresheet_with_calculated_totals(self):
        data = {**management_form("yamb_scoresheets", 1), **self.sheet_data("yamb_scoresheets", 0, self.anna, COMPLETE_SHEET)}
        response = self.client.post(reverse("scores:new_yamb"), data)

        game = YambGame.objects.get()
        self.assertRedirects(
            response, f"{reverse('scores:new_game')}?yamb_game_id={game.pk}", fetch_redirect_response=False
        )
        sheet = game.yamb_scoresheets.get()
        self.assertEqual(sheet.player, self.anna)
        self.assertEqual(sheet.final_score, COMPLETE_SHEET_FINAL_SCORE)
        self.assertEqual(sheet.row_2_total, 20)
        self.assertEqual(sheet.row_h_total, 106)

    def test_new_yamb_with_invalid_value_saves_nothing(self):
        data = {
            **management_form("yamb_scoresheets", 1),
            **self.sheet_data("yamb_scoresheets", 0, self.anna, {**COMPLETE_SHEET, "row_1_down": 6}),
        }
        response = self.client.post(reverse("scores:new_yamb"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(YambGame.objects.count(), 0)

    def test_edit_scoresheet_updates_values_and_totals(self):
        game = make_yamb_game([self.anna])
        sheet = game.yamb_scoresheets.get()
        data = {"player": self.anna.pk, **{**COMPLETE_SHEET, "row_p_down": 0}}

        response = self.client.post(reverse("scores:edit_yamb_scoresheet", args=[game.pk, sheet.pk]), data)

        self.assertRedirects(
            response, f"{reverse('scores:new_game')}?yamb_game_id={game.pk}", fetch_redirect_response=False
        )
        sheet.refresh_from_db()
        self.assertEqual(sheet.row_p_total, 0)
        self.assertEqual(sheet.final_score, COMPLETE_SHEET_FINAL_SCORE - 100)

    def test_delete_one_of_two_scoresheets_keeps_game(self):
        game = make_yamb_game([self.anna, self.bram])
        sheet = game.yamb_scoresheets.get(player=self.anna)

        response = self.client.post(reverse("scores:delete_yamb_scoresheet", args=[game.pk, sheet.pk]))

        self.assertRedirects(response, reverse("scores:yamb_detail", args=[game.pk]))
        self.assertEqual(list(game.yamb_scoresheets.values_list("player__name", flat=True)), ["Bram"])

    def test_delete_last_scoresheet_deletes_game(self):
        game = make_yamb_game([self.anna])
        sheet = game.yamb_scoresheets.get()

        response = self.client.post(reverse("scores:delete_yamb_scoresheet", args=[game.pk, sheet.pk]))

        self.assertRedirects(response, reverse("scores:yamb_list"))
        self.assertFalse(YambGame.objects.exists())
        self.assertFalse(YambScoresheet.objects.exists())


class YambPlayerPostTests(TestCase):
    def test_new_player_is_saved_title_cased(self):
        response = self.client.post(reverse("scores:new_player"), {"name": "  dora  "})

        self.assertRedirects(response, reverse("scores:player_list"))
        self.assertTrue(Player.objects.filter(name="Dora").exists())

    def test_duplicate_player_name_is_rejected_case_insensitive(self):
        make_player("Dora")
        response = self.client.post(reverse("scores:new_player"), {"name": "DORA"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.count(), 1)

    def test_edit_player_renames(self):
        player = make_player("Cara")
        response = self.client.post(reverse("scores:edit_player", args=[player.pk]), {"name": "Carla"})

        self.assertRedirects(response, reverse("scores:player_list"))
        player.refresh_from_db()
        self.assertEqual(player.name, "Carla")

    def test_delete_player_removes_player(self):
        player = make_player("Cara")
        response = self.client.post(reverse("scores:delete_player", args=[player.pk]))

        self.assertRedirects(response, reverse("scores:player_list"))
        self.assertFalse(Player.objects.filter(pk=player.pk).exists())

    def test_delete_page_get_does_not_delete(self):
        player = make_player("Cara")
        self.client.get(reverse("scores:delete_player", args=[player.pk]))
        self.assertTrue(Player.objects.filter(pk=player.pk).exists())
