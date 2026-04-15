from django.urls import path
from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.index, name='index'),
    path('games/', views.game_list, name='game_list'),
    path('new/', views.new_game, name='new_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('player-stats/', views.player_stats, name='player_stats'),
    path('statistics/', views.yamb_statistics, name='yamb_statistics'),
    path('dashboard/', views.yamb_dashboard, name='yamb_dashboard'),
    
    # Player management
    path('players/', views.player_list, name='player_list'),
    path('players/new/', views.new_player, name='new_player'),
    path('players/<int:pk>/edit/', views.edit_player, name='edit_player'),
    path('players/<int:pk>/delete/', views.delete_player, name='delete_player'),
    
    # Yamb scoresheet routes
    path('yamb/', views.yamb_list, name='yamb_list'),
    path('yamb/new/', views.new_yamb, name='new_yamb'),
    path('yamb/<int:pk>/', views.yamb_detail, name='yamb_detail'),
    path('yamb/<int:game_pk>/edit/<int:scoresheet_pk>/', views.edit_yamb_scoresheet, name='edit_yamb_scoresheet'),
    path('yamb/<int:game_pk>/delete/<int:scoresheet_pk>/', views.delete_yamb_scoresheet, name='delete_yamb_scoresheet'),
]
