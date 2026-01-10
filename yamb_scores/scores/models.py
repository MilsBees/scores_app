from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Game(models.Model):
    played_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Game #{self.id} on {self.played_at.strftime('%Y-%m-%d %H:%M')}"

class Score(models.Model):
    game = models.ForeignKey(Game, related_name='scores', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='scores', on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.player} — {self.score} (Game {self.game_id})"
