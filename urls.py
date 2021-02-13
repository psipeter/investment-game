from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.startGame, name='game'),
    path('updateGame', views.updateGame, name="updateGame"),
    path('tutorial', views.tutorial, name="tutorial"),
    path('stats', views.stats, name="stats"),
    path('cash_out', views.cash_out, name="cash_out"),
    path('feedback', views.feedback, name="feedback"),
    path('information', views.information, name='information'),
    path('consent_register', views.consent_register, name='consent_register'),
    path('consent_signed', views.consent_signed, name='consent_signed'),
    path('survey', views.survey, name='survey'),
]