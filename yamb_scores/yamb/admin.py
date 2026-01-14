from django.contrib import admin
from .models import Player, Game, Score

class ScoreInline(admin.TabularInline):
    model = Score
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'played_at')
    inlines = [ScoreInline]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'score', 'game')
    list_filter = ('player',)
