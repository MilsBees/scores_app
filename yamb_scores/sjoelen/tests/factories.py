"""Small helpers that create realistic Sjoelen data for tests."""
from datetime import timedelta

from django.utils import timezone

from sjoelen.models import SjoelenGame, SjoelenPlayer, SjoelenScore


def make_player(name):
    return SjoelenPlayer.objects.create(name=name)


def make_game(rounds_by_player, days_ago=0):
    """Create a game from {player: (round_1, round_2, round_3)}, played `days_ago` days ago."""
    game = SjoelenGame.objects.create()
    SjoelenGame.objects.filter(pk=game.pk).update(played_at=timezone.now() - timedelta(days=days_ago))
    for player, (r1, r2, r3) in rounds_by_player.items():
        SjoelenScore.objects.create(game=game, player=player, round_1=r1, round_2=r2, round_3=r3)
    return game


def make_sjoelen_dataset():
    """Three players with 6 games each, so they appear on the leaderboard."""
    anna, bram, cleo = make_player("Anna"), make_player("Bram"), make_player("Cleo")
    for day in range(6):
        make_game(
            {anna: (40 + day, 38, 45), bram: (30, 35 - day, 28), cleo: (50, 20, 33 + day)},
            days_ago=day * 15,
        )
    return anna, bram, cleo
