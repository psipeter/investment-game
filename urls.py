from django.urls import path
from . import views

urlpatterns = [
    path('game/<str:gameID>/', views.game, name='game'),
	path('newgame', views.newgame, name='newgame'),
	path('game_complete/<str:gameID>/', views.game_complete, name='game_complete'),
]