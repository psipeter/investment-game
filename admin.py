from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
from .models import Game, Agent, User

# admin.site.register(Game)
@admin.register(Game)
class Game(admin.ModelAdmin):
	list_display = ('uuid',
		'user', 'userRole', 'userScore',
		'get_agent', 'agentRole', 'agentScore',
		'date', 'userMoves', 'agentMoves')
	ordering = ('-date',)
	def get_agent(self, obj):
		return obj.agent.agentType
	get_agent.short_description = "Agent"
	get_agent.admin_order_field = "agent__agentType"

@admin.register(Agent)
class Agent(admin.ModelAdmin):
	list_display = ('agentType','uuid')

@admin.register(User)
class User(UserAdmin):
	list_display = ('username', 'currentGame', 'age', 'gender', 'income', 'education', 'veteran', 'empathy', 'risk', 'altruism')