from django.urls import path
from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('new/', views.new_game, name='new_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
