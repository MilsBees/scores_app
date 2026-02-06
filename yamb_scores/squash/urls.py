from django.urls import path
from . import views

app_name = 'squash'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_match, name='new_match'),
    path('session/new/', views.new_session, name='new_session'),
    path('matches/', views.match_list, name='match_list'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('h2h/', views.h2h, name='h2h'),
]
