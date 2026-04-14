from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class SjoelenPlayer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(Lower("name"), name="sjoelenplayer_name_ci_unique"),
        ]

    def __str__(self):
        return self.name


class SjoelenGame(models.Model):
    """A Sjoelen game session with scores for multiple players"""
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        players = self.scores.values_list('player__name', flat=True)
        return f"Sjoelen Game #{self.id} - {', '.join(players) or 'No players'}"

    class Meta:
        ordering = ['-played_at']


class SjoelenScore(models.Model):
    """Score for one player in a Sjoelen game"""
    game = models.ForeignKey(SjoelenGame, related_name='scores', on_delete=models.CASCADE)
    player = models.ForeignKey(SjoelenPlayer, related_name='scores', on_delete=models.CASCADE)
    
    round_1 = models.IntegerField(null=True, blank=True)
    round_2 = models.IntegerField(null=True, blank=True)
    round_3 = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-game_id']

    def __str__(self):
        return f"{self.player} - Game {self.game_id}"

    @property
    def final_score(self):
        """Calculate final score as sum of all rounds"""
        total = 0
        if self.round_1 is not None:
            total += self.round_1
        if self.round_2 is not None:
            total += self.round_2
        if self.round_3 is not None:
            total += self.round_3
        return total
