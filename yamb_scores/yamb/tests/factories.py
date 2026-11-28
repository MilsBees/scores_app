"""Small helpers that create realistic Yamb data for tests."""
from datetime import timedelta

from django.utils import timezone

from yamb.models import Game, Player, Score, YambGame, YambScoresheet

# A fully filled-in scoresheet that passes every form rule.
# Expected totals (current scoring rules):
#   rows 1-6: (sum - 12) * row number * 10 -> 0, 20, 0, -40, 0, 120
#   H: 28+27+26+25 = 106 (no H+L column reaches 50, so no bonus); L: 6+7+8+9 = 30
#   FH: 120, C: 120, S: 80, P: 100
#   final score: 656
COMPLETE_SHEET = {
    "row_1_down": 3, "row_1_up": 3, "row_1_l": 3, "row_1_s": 3,
    "row_2_down": 4, "row_2_up": 3, "row_2_l": 3, "row_2_s": 3,
    "row_3_down": 3, "row_3_up": 3, "row_3_l": 3, "row_3_s": 3,
    "row_4_down": 2, "row_4_up": 3, "row_4_l": 3, "row_4_s": 3,
    "row_5_down": 3, "row_5_up": 3, "row_5_l": 3, "row_5_s": 3,
    "row_6_down": 5, "row_6_up": 3, "row_6_l": 3, "row_6_s": 3,
    "row_h_down": 28, "row_h_up": 27, "row_h_l": 26, "row_h_s": 25,
    "row_l_down": 6, "row_l_up": 7, "row_l_l": 8, "row_l_s": 9,
    "row_fh_down": 40, "row_fh_up": 0, "row_fh_l": 40, "row_fh_s": 40,
    "row_c_down": 60, "row_c_up": 0, "row_c_l": 0, "row_c_s": 60,
    "row_s_down": 0, "row_s_up": 80, "row_s_l": 0, "row_s_s": 0,
    "row_p_down": 100, "row_p_up": 0, "row_p_l": 0, "row_p_s": 0,
}
COMPLETE_SHEET_FINAL_SCORE = 656


def make_player(name):
    return Player.objects.create(name=name)


def make_game(scores, days_ago=0):
    """Create a simple Game with {player: score} results, played `days_ago` days ago."""
    game = Game.objects.create()
    Game.objects.filter(pk=game.pk).update(played_at=timezone.now() - timedelta(days=days_ago))
    for player, score in scores.items():
        Score.objects.create(game=game, player=player, score=score)
    return game


def make_yamb_game(players, final_scores=None):
    """Create a YambGame with one complete scoresheet per player."""
    game = YambGame.objects.create()
    for index, player in enumerate(players):
        final_score = final_scores[index] if final_scores else COMPLETE_SHEET_FINAL_SCORE
        YambScoresheet.objects.create(game=game, player=player, final_score=final_score, **COMPLETE_SHEET)
    return game


def make_yamb_dataset():
    """Three players with enough games to appear on leaderboards (5+ games each)."""
    anna, bram, cleo = make_player("Anna"), make_player("Bram"), make_player("Cleo")
    for day in range(6):
        make_game({anna: 600 + day * 10, bram: 550 - day * 5, cleo: 500 + day}, days_ago=day * 20)
    make_yamb_game([anna, bram], final_scores=[656, 610])
    make_yamb_game([cleo])
    return anna, bram, cleo
