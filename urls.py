from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.startGame, name='game'),
    path('continue/', views.continueGame, name='continue'),
    path('updateGame', views.updateGame, name="updateGame")
]