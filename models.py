from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import datetime

import uuid
import numpy as np
import random
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import mpld3
import json

from .agents import *
from .experiments import *
from .parameters import *


popA = ['T4T']
popB = ['T4T']

class Feedback(models.Model):
	text = models.CharField(max_length=4200, blank=True, null=True, default=str)

class Blob(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True, default=str)
	blob = models.BinaryField(null=True)  # for agent class

class Agent(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique agent ID")
	name = models.CharField(max_length=100, blank=True, null=True, default=str)
	created = models.DateTimeField(auto_now_add=True)
	player = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	blob = models.ForeignKey(Blob, on_delete=models.SET_NULL, null=True, blank=True)
	obj = None  # will store de-pickled blob, the python agent class

	def start(self, name, player):
		self.name = name
		self.player = player
		self.save()

	def getObj(self, game):
		name = self.name
		player = self.player
		blobname = f"{name}{player}"
		nA = int(game.capital+1) if player == "A" else int(game.capital*game.match+1)
		nS = 10
		if Blob.objects.filter(name=blobname).exists():
			print(f"loaded blob named {blobname}")
			self.blob = Blob.objects.get(name=blobname)
			self.obj = pickle.loads(self.blob.blob)
		else:
			print(f"creating new blob named {blobname}")
			if name=='Greedy':
				self.obj = Greedy(player)
			elif name=="Generous":
				self.obj = Generous(player)
			elif name=="tutorial":
				self.obj = T4T(player, F=1, P=1)
			elif name=="required":
				self.obj = T4T(player, F=1, P=1)
			elif name=="T4T-forgive":
				# self.obj = T4T(player, F=1.5, P=1)
				self.obj = T4T(player, F=1, P=0.5)
			elif name=="T4T-punish":
				self.obj = T4T(player, F=0.5, P=1)
				# self.obj = T4T(player, F=1, P=1.5)
			elif name=="Bandit":
				self.obj = Bandit(player, nA)  # rO=?
			elif name=="QLearn":
				self.obj = QLearn(player, nA, nS)
			elif name=="Wolf":
				self.obj = Wolf(player, nA, nS)
			elif name=="Hill":
				self.obj = Hill(player, nA, nS)
			elif name=="ModelBased":
				self.obj = ModelBased(player, nA, nS)
			else:
				raise Exception(f'{name} is not a valid agent class')
			self.blob = Blob.objects.create()
			self.blob.name = blobname
			self.blob.blob = pickle.dumps(self.obj)
		self.obj.loadArchive(file=f"{name}{player}.npz")
		self.obj.reset()
		agentStates = game.historyToArray("agent", "state")
		if len(agentStates) > 0:
			self.obj.state = agentStates[-1]
		self.blob.save()
		self.save()

	def learn(self, game):
		# update matrices in python object
		history = game.historyToDict()
		self.getObj(game, history)
		self.obj.learn(history)
		# update matricies in database
		self.blob.blob = pickle.dumps(self.obj)
		self.blob.save()
		self.save()


class Game(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique game ID")
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
	userGives = models.CharField(max_length=50, blank=True, null=True, default=str)
	userKeeps = models.CharField(max_length=50, blank=True, null=True, default=str)
	userRewards = models.CharField(max_length=50, blank=True, null=True, default=str)
	userTimes = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentGives = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentKeeps = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentRewards = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentStates = models.CharField(max_length=50, blank=True, null=True, default=str)
	userRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	agentRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	complete = models.BooleanField(default=False)
	rounds = models.IntegerField(default=ROUNDS)
	capital = models.IntegerField(default=CAPITAL)
	match = models.FloatField(default=MATCH)
	seed = models.IntegerField(default=0)

	def setAgent(self):
		if not self.user.doneTutorial:
			name = "tutorial"
		elif not self.user.doneRequired:
			name = "required"
		elif self.user.group == "1":
			name = "T4T-forgive"
		elif self.user.group == "2":
			name = "T4T-punish"
		else:
			raise "agent not set"
		self.agent = Agent.objects.create()
		self.agent.start(name, self.agentRole)
		self.save()

	def start(self, user):
		self.user = user
		self.seed = np.random.randint(1e6)
		np.random.seed(self.seed)  # set random number seed
		if np.random.rand() > 0.5:
			self.userRole = "A"
			self.agentRole = "B"
		else:
			self.userRole = "B"
			self.agentRole = "A"
		self.setAgent()
		if self.agentRole == "A":
			self.goAgent(self.capital)
		self.user.currentGame = self
		self.user.save()
		self.save()

	def step(self, userGive, userKeep, userTime):
		self.goUser(userGive, userKeep, userTime)
		if self.userRole == "A":
			invest = self.historyToArray("user", "give")[-1]
			self.goAgent(self.match*invest)
		elif not self.complete:
			self.goAgent(self.capital)
		self.rewards()

	def goUser(self, userGive, userKeep, userTime):
		self.userGives += f"{userGive:d},"
		self.userKeeps += f"{userKeep:d},"
		self.userTimes += f"{userTime:.2f},"
		self.checkComplete()

	def goAgent(self, money):
		history = self.historyToDict()
		self.agent.getObj(self)
		# print(self.agent.obj.Q)
		# print(self.agent.obj.pi)
		agentGive, agentKeep = self.agent.obj.act(money, history)
		agentState = self.agent.obj.state
		self.agentGives += f"{agentGive:d},"
		self.agentKeeps += f"{agentKeep:d},"
		self.agentStates += f"{agentState:.1f}"
		self.checkComplete()

	def checkComplete(self):
		userGives = self.historyToArray("user", "give")
		agentGives = self.historyToArray("agent", "give")
		if len(userGives) == self.rounds and len(agentGives) == self.rounds:
			self.complete = True
		if len(userGives) > self.rounds or len(agentGives) > self.rounds:
			raise Exception("Too many moves taken")
		self.save()

	def rewards(self):
		userGives = self.historyToArray("user", "give")
		userKeeps = self.historyToArray("user", "keep")
		agentGives = self.historyToArray("agent", "give")
		agentKeeps = self.historyToArray("agent", "keep")
		self.userRewards = ""
		self.agentRewards = ""
		self.save()
		for t in range(len(userGives)):
			if self.userRole == "A":
				self.userRewards += f"{userKeeps[t]+agentGives[t]:d},"
				self.agentRewards += f"{agentKeeps[t]:d},"
			else:
				self.agentRewards += f"{agentKeeps[t]+userGives[t]:d},"
				self.userRewards += f"{userKeeps[t]:d},"
		self.save()

	def historyToArray(self, player, entry):
		if player == "user":
			if entry == "give":
				return np.array(self.userGives.split(',')[:-1]).astype(np.int)
			elif entry == "keep":
				return np.array(self.userKeeps.split(',')[:-1]).astype(np.int)
			elif entry == "reward":
				return np.array(self.userRewards.split(',')[:-1]).astype(np.int)
			elif entry == "state":
				return np.zeros_like(self.agentStates.split(',')[:-1])
		else:
			if entry == "give":
				return np.array(self.agentGives.split(',')[:-1]).astype(np.int)
			elif entry == "keep":
				return np.array(self.agentKeeps.split(',')[:-1]).astype(np.int)
			elif entry == "reward":
				return np.array(self.agentRewards.split(',')[:-1]).astype(np.int)
			elif entry == "state":
				return np.array(self.agentStates.split(',')[:-1])

	def historyToDict(self):
		A = "user" if self.userRole=="A" else "agent"
		B = "agent" if self.userRole=="A" else "user"
		history = {
			'aGives': self.historyToArray(A, "give"),
			'aKeeps': self.historyToArray(A, "keep"),
			'aRewards': self.historyToArray(A, "reward"),
			'aStates': self.historyToArray(A, "state"),
			'bGives': self.historyToArray(B, "give"),
			'bKeeps': self.historyToArray(B, "keep"),
			'bRewards': self.historyToArray(B, "reward"),
			'bStates': self.historyToArray(B, "state"),
		}
		return history


class User(AbstractUser):
	# assign to unique group
	def f():
		return 1 if np.random.rand() < 0.5 else 2
	currentGame = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="currentGame")
	nRequired = models.IntegerField(default=0)
	nBonus = models.IntegerField(default=0)
	doneConsent = models.DateTimeField(null=True, blank=True)
	doneSurvey = models.DateTimeField(null=True, blank=True)
	doneTutorial = models.DateTimeField(null=True, blank=True)
	doneRequired = models.DateTimeField(null=True, blank=True)
	doneBonus = models.DateTimeField(null=True, blank=True)
	doneCash = models.DateTimeField(null=True, blank=True)
	group = models.CharField(max_length=1, choices=(("1", "forgive"), ("2", "punish")), default=f)
	code = models.CharField(max_length=32, default=get_random_string(length=32), help_text="MTurk Confirmation Code")
	age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(120)], null=True, blank=True)
	gender = models.CharField(max_length=300, null=True, blank=True)
	income = models.CharField(max_length=300, null=True, blank=True)
	education = models.CharField(max_length=300, null=True, blank=True)
	veteran = models.CharField(max_length=300, null=True, blank=True)
	empathy = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True, blank=True)
	risk = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True, blank=True)
	altruism = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True, blank=True)

	def setProgress(self):
		nRequired = Game.objects.filter(user=self, complete=True, agent__name="required").count()
		nBonus = Game.objects.filter(user=self, complete=True).exclude(agent__name="required").count()
		self.nRequired = nRequired
		self.nBonus = nBonus
		self.save()
		if self.nRequired < N_REQUIRED:
			self.doneRequired = None
		if self.nBonus < N_BONUS:
			self.doneBonus = None
		self.save()
		if self.doneRequired == None and self.nRequired >= N_REQUIRED:
			self.doneRequired = datetime.now()
		if self.doneBonus == None and self.nBonus >= N_BONUS:
			self.doneBonus = datetime.now()
		self.save()

	def makeFigs(self):
		gamesA = Game.objects.filter(user=self, userRole="A", complete=True).exclude(agent__name="required")
		gamesB = Game.objects.filter(user=self, userRole="B", complete=True).exclude(agent__name="required")
		if gamesA.count() <= 1 or gamesB.count() <= 1:
			return {'skip': True, 'figScoreA': None, 'figScoreB': None, 'figGenA': None, 'figGenB': None}
		dfs = []
		columns = ('player', 'turn', 'score', 'generosity')
		for game in gamesA:
			for t in range(game.rounds):
				give = game.historyToArray("user", "give")
				keep = game.historyToArray("user", "keep")
				reward = game.historyToArray("user", "reward")
				dfs.append(pd.DataFrame([["A", t, reward[t], give[t]/(give[t]+keep[t])]], columns=columns))
		for game in gamesB:
			for t in range(game.rounds):
				give = game.historyToArray("user", "give")
				keep = game.historyToArray("user", "keep")
				reward = game.historyToArray("user", "reward")
				dfs.append(pd.DataFrame([["B", t, reward[t], give[t]/(give[t]+keep[t])]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)

		ylim = ((0, 1))
		binsG = np.linspace(0, 1, game.capital+1)
		binsS = np.arange(0, game.match*game.capital+1, 2)
		meanScore = np.mean(df['score'])

		fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=((8, 4)))
		sns.histplot(data=df, x='score', ax=ax, stat="probability", bins=binsS, element="step", hue='player')  
		ax.set(xlabel="Score", ylabel="Frequency", xticks=((binsS)), ylim=ylim, title="Score")
		ax.plot([BONUS_THR, BONUS_THR], [0,1], color='k', linestyle="--", label="Bonus Threshold")
		ax.plot([meanScore, meanScore], [0,1], color='r' if meanScore < BONUS_THR else 'g', label="Current Score")
		sns.histplot(data=df, x='generosity', ax=ax2, stat="probability", bins=binsG, element="step", hue='player')  
		ax2.set(xlabel="Generosity", ylabel=None, xticks=((binsG)), title="Generosity")
		leg = ax.legend(loc='upper right')
		# leg2 = ax2.legend(loc='upper right')
		fig.tight_layout()
		fig.savefig('game/plots/userStats.pdf')
		figure = mpld3.fig_to_html(fig)
		plt.close()

		return {'skip': False, 'figure': figure}
