from django.urls import path
from . import views

app_name = 'sjoelen'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_game, name='new_game'),
    path('games/', views.game_list, name='game_list'),
    path('players/', views.player_list, name='player_list'),
    path('players/new/', views.new_player, name='new_player'),
    path('players/<int:pk>/edit/', views.edit_player, name='edit_player'),
    path('players/<int:pk>/delete/', views.delete_player, name='delete_player'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('player-stats/', views.player_stats, name='player_stats'),
    path('statistics/', views.statistics, name='statistics'),
]
