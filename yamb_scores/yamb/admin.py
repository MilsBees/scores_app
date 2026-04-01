from django.contrib import admin
from .models import Player, Game, Score, YambGame, YambScoresheet

class ScoreInline(admin.TabularInline):
    model = Score
    extra = 1

class YambScoreSheetInline(admin.TabularInline):
    model = YambScoresheet
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

@admin.register(YambGame)
class YambGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    inlines = [YambScoreSheetInline]

@admin.register(YambScoresheet)
class YambScoreSheetAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'final_score')
    list_filter = ('player', 'game')
