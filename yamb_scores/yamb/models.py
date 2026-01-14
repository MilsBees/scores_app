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


class YambGame(models.Model):
    """A Yamb game session with scoresheet(s)"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        players = self.yamb_scoresheets.values_list('player__name', flat=True)
        return f"Yamb Game #{self.id} - {', '.join(players) or 'No players'}"

class YambScoresheet(models.Model):
    """Individual scoresheet for one player in a Yamb game"""
    game = models.ForeignKey(YambGame, related_name='yamb_scoresheets', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='yamb_scoresheets', on_delete=models.CASCADE)
    
    # Row 1
    row_1_down = models.IntegerField(null=True, blank=True)
    row_1_up = models.IntegerField(null=True, blank=True)
    row_1_l = models.IntegerField(null=True, blank=True)
    row_1_s = models.IntegerField(null=True, blank=True)
    row_1_total = models.IntegerField(null=True, blank=True)
    
    # Row 2
    row_2_down = models.IntegerField(null=True, blank=True)
    row_2_up = models.IntegerField(null=True, blank=True)
    row_2_l = models.IntegerField(null=True, blank=True)
    row_2_s = models.IntegerField(null=True, blank=True)
    row_2_total = models.IntegerField(null=True, blank=True)
    
    # Row 3
    row_3_down = models.IntegerField(null=True, blank=True)
    row_3_up = models.IntegerField(null=True, blank=True)
    row_3_l = models.IntegerField(null=True, blank=True)
    row_3_s = models.IntegerField(null=True, blank=True)
    row_3_total = models.IntegerField(null=True, blank=True)
    
    # Row 4
    row_4_down = models.IntegerField(null=True, blank=True)
    row_4_up = models.IntegerField(null=True, blank=True)
    row_4_l = models.IntegerField(null=True, blank=True)
    row_4_s = models.IntegerField(null=True, blank=True)
    row_4_total = models.IntegerField(null=True, blank=True)
    
    # Row 5
    row_5_down = models.IntegerField(null=True, blank=True)
    row_5_up = models.IntegerField(null=True, blank=True)
    row_5_l = models.IntegerField(null=True, blank=True)
    row_5_s = models.IntegerField(null=True, blank=True)
    row_5_total = models.IntegerField(null=True, blank=True)
    
    # Row 6
    row_6_down = models.IntegerField(null=True, blank=True)
    row_6_up = models.IntegerField(null=True, blank=True)
    row_6_l = models.IntegerField(null=True, blank=True)
    row_6_s = models.IntegerField(null=True, blank=True)
    row_6_total = models.IntegerField(null=True, blank=True)
    
    # Row H
    row_h_down = models.IntegerField(null=True, blank=True)
    row_h_up = models.IntegerField(null=True, blank=True)
    row_h_l = models.IntegerField(null=True, blank=True)
    row_h_s = models.IntegerField(null=True, blank=True)
    row_h_total = models.IntegerField(null=True, blank=True)
    
    # Row L
    row_l_down = models.IntegerField(null=True, blank=True)
    row_l_up = models.IntegerField(null=True, blank=True)
    row_l_l = models.IntegerField(null=True, blank=True)
    row_l_s = models.IntegerField(null=True, blank=True)
    row_l_total = models.IntegerField(null=True, blank=True)
    
    # Row FH
    row_fh_down = models.IntegerField(null=True, blank=True)
    row_fh_up = models.IntegerField(null=True, blank=True)
    row_fh_l = models.IntegerField(null=True, blank=True)
    row_fh_s = models.IntegerField(null=True, blank=True)
    row_fh_total = models.IntegerField(null=True, blank=True)
    
    # Row C
    row_c_down = models.IntegerField(null=True, blank=True)
    row_c_up = models.IntegerField(null=True, blank=True)
    row_c_l = models.IntegerField(null=True, blank=True)
    row_c_s = models.IntegerField(null=True, blank=True)
    row_c_total = models.IntegerField(null=True, blank=True)
    
    # Row S
    row_s_down = models.IntegerField(null=True, blank=True)
    row_s_up = models.IntegerField(null=True, blank=True)
    row_s_l = models.IntegerField(null=True, blank=True)
    row_s_s = models.IntegerField(null=True, blank=True)
    row_s_total = models.IntegerField(null=True, blank=True)
    
    # Row P
    row_p_down = models.IntegerField(null=True, blank=True)
    row_p_up = models.IntegerField(null=True, blank=True)
    row_p_l = models.IntegerField(null=True, blank=True)
    row_p_s = models.IntegerField(null=True, blank=True)
    row_p_total = models.IntegerField(null=True, blank=True)
    
    # Final score entered by user (separate from scoresheet totals)
    final_score = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('game', 'player')
    
    def __str__(self):
        return f"{self.player.name} - Yamb Game #{self.game_id}"
