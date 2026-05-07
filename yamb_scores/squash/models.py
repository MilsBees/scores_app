from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class SquashSession(models.Model):
    date_played = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_played"]
        verbose_name = "Squash session"
        verbose_name_plural = "Squash sessions"

    def __str__(self):
        return f"Squash Session - {self.date_played}"


class SquashPlayer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(Lower("name"), name="squashplayer_name_ci_unique"),
        ]

    def __str__(self):
        return self.name

class SquashMatch(models.Model):
    class SetType(models.TextChoices):
        ELEVEN = "11", "11-point"
        TWENTY_ONE = "21", "21-point"

    session = models.ForeignKey(
        SquashSession,
        related_name="matches",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    player_1 = models.ForeignKey(SquashPlayer, related_name='squash_matches_as_p1', on_delete=models.CASCADE)
    player_2 = models.ForeignKey(SquashPlayer, related_name='squash_matches_as_p2', on_delete=models.CASCADE)
    date_played = models.DateField()
    set_type = models.CharField(
        max_length=2,
        choices=SetType.choices,
        default=SetType.ELEVEN,
        help_text="Point target for sets in this match (11 or 21)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player_1.name} vs {self.player_2.name} - {self.date_played}"

    class Meta:
        ordering = ['-date_played']
        verbose_name = 'Squash match'
        verbose_name_plural = 'Squash matches'

class SquashSet(models.Model):
    match = models.ForeignKey(SquashMatch, related_name='sets', on_delete=models.CASCADE)
    set_number = models.IntegerField()
    player_1_points = models.IntegerField()
    player_2_points = models.IntegerField()
    is_incomplete = models.BooleanField(
        default=False,
        help_text="Automatically set if neither player reached the minimum score for the match's set type",
    )

    class Meta:
        ordering = ['set_number']

    def __str__(self):
        return f"{self.match} - Set {self.set_number}: {self.player_1_points}-{self.player_2_points}"

    def save(self, *args, **kwargs):
        # Auto-calculate is_incomplete based on set type
        min_score = int(self.match.set_type)  # "11" -> 11, "21" -> 21
        max_points = max(self.player_1_points, self.player_2_points)
        self.is_incomplete = max_points < min_score
        super().save(*args, **kwargs)

    @property
    def winner(self):
        if self.player_1_points > self.player_2_points:
            return self.match.player_1
        elif self.player_2_points > self.player_1_points:
            return self.match.player_2
        return None
