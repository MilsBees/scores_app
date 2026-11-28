"""Sjoelen scoring rules (as currently implemented)."""
from unittest import expectedFailure

from django.test import TestCase
from django.urls import reverse

from sjoelen.models import SjoelenScore

from .factories import make_game, make_player


class SjoelenFinalScoreTests(TestCase):
    def test_final_score_is_sum_of_rounds(self):
        self.assertEqual(SjoelenScore(round_1=40, round_2=38, round_3=45).final_score, 123)

    def test_missing_rounds_count_as_zero(self):
        self.assertEqual(SjoelenScore(round_1=40, round_2=None, round_3=45).final_score, 85)
        self.assertEqual(SjoelenScore().final_score, 0)


class SjoelenLeaderboardUsesSameTotalsTests(TestCase):
    def test_leaderboard_best_score_matches_final_score(self):
        anna = make_player("Anna")
        for day in range(5):
            make_game({anna: (40, 38, 45 + day)}, days_ago=day)

        response = self.client.get(reverse("sjoelen:leaderboard") + "?show_all=true")

        best = max(s.final_score for s in SjoelenScore.objects.all())
        self.assertEqual(best, 127)
        player = next(p for p in response.context["players"] if p.name == "Anna")
        self.assertEqual(player.best_score, best)

    @expectedFailure  # Known bug: sjoelen-002. Remove this marker when it's fixed.
    def test_game_with_blank_round_counts_in_leaderboard_like_everywhere_else(self):
        # The game form allows leaving a round blank. final_score (used by the top-scores
        # list and the median) counts it as 0, but the leaderboard's best/average is summed
        # in SQL, where a blank round makes the whole game total NULL, so it's ignored.
        anna = make_player("Anna")
        for day in range(5):
            make_game({anna: (40, 40, 40)}, days_ago=day)
        make_game({anna: (90, None, 90)}, days_ago=9)  # final_score 180

        response = self.client.get(reverse("sjoelen:leaderboard") + "?show_all=true")

        player = next(p for p in response.context["players"] if p.name == "Anna")
        self.assertEqual(player.games_played, 6)
        self.assertEqual(player.best_score, 180)
        self.assertEqual(player.avg_score, (5 * 120 + 180) / 6)
