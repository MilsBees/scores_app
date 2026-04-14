from django.contrib import admin
from .models import SjoelenPlayer, SjoelenGame, SjoelenScore


@admin.register(SjoelenPlayer)
class SjoelenPlayerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(SjoelenGame)
class SjoelenGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'played_at')
    list_filter = ('played_at',)
    ordering = ('-played_at',)


@admin.register(SjoelenScore)
class SjoelenScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'player', 'round_1', 'round_2', 'round_3', 'final_score')
    list_filter = ('game__played_at', 'player')
    search_fields = ('player__name',)
    ordering = ('-game_id',)
