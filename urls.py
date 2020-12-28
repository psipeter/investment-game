from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.startGame, name='game'),
    path('updateGame', views.updateGame, name="updateGame")
]