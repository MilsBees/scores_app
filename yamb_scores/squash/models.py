from django.db import models

class SquashPlayer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SquashMatch(models.Model):
    player_1 = models.ForeignKey(SquashPlayer, related_name='squash_matches_as_p1', on_delete=models.CASCADE)
    player_2 = models.ForeignKey(SquashPlayer, related_name='squash_matches_as_p2', on_delete=models.CASCADE)
    date_played = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player_1.name} vs {self.player_2.name} - {self.date_played}"

    class Meta:
        ordering = ['-date_played']

class SquashSet(models.Model):
    match = models.ForeignKey(SquashMatch, related_name='sets', on_delete=models.CASCADE)
    set_number = models.IntegerField()
    player_1_points = models.IntegerField()
    player_2_points = models.IntegerField()

    class Meta:
        ordering = ['set_number']

    def __str__(self):
        return f"{self.match} - Set {self.set_number}: {self.player_1_points}-{self.player_2_points}"

    @property
    def winner(self):
        if self.player_1_points > self.player_2_points:
            return self.match.player_1
        elif self.player_2_points > self.player_1_points:
            return self.match.player_2
        return None
