from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Game

# admin.site.register(Game)
@admin.register(Game)
class Game(admin.ModelAdmin):
	list_display = ('id',
		'user', 'userRole', 'userScore',
		'agent', 'agentRole', 'agentScore',
		'date', 'userMoves', 'agentMoves')
	ordering = ('-date',)

def age(obj):
	return str(obj.profile.age)
def gender(obj):
	return str(obj.profile.gender)
def income(obj):
	return str(obj.profile.income)
def education(obj):
	return str(obj.profile.education)
def veteran(obj):
	return str(obj.profile.veteran)
def empathy(obj):
	return str(obj.profile.empathy)
def risk(obj):
	return str(obj.profile.risk)
def altruism(obj):
	return str(obj.profile.altruism)

UserAdmin.list_display = ('username', age, gender, income, education, veteran, empathy, risk, altruism)