from django.urls import path
from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('new/', views.new_game, name='new_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Yamb scoresheet routes
    path('yamb/', views.yamb_list, name='yamb_list'),
    path('yamb/new/', views.new_yamb, name='new_yamb'),
    path('yamb/<int:pk>/', views.yamb_detail, name='yamb_detail'),
    path('yamb/<int:game_pk>/edit/<int:scoresheet_pk>/', views.edit_yamb_scoresheet, name='edit_yamb_scoresheet'),
    path('yamb/<int:game_pk>/delete/<int:scoresheet_pk>/', views.delete_yamb_scoresheet, name='delete_yamb_scoresheet'),
]
