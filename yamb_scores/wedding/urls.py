from django.urls import include, path

from . import views

app_name = 'wedding'
WEDDING_URL_PREFIX = 'wedding/'

board_urls = [
    path('', views.board, name='board'),
    path('logout/', views.logout_view, name='logout'),
    path('api/board/', views.board_api, name='api_board'),
    path('api/cards/', views.cards_api, name='api_cards'),
    path('api/cards/<int:card_id>/', views.card_api, name='api_card'),
    path('api/cards/<int:card_id>/move/', views.move_card_api, name='api_move_card'),
]

urlpatterns = [
    path(WEDDING_URL_PREFIX, include([
        path('login/', views.login_view, name='login'),
        path('', include(board_urls)),
    ])),
]
