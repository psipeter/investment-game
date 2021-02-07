from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.crypto import get_random_string

import uuid
import numpy as np
import random
import pickle

from .agents import *
from .experiments import *


popA = ['T4T']
popB = ['T4T']

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
			elif name=="T4T":
				self.obj = T4T(player)  # F=?
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
	rounds = models.IntegerField(default=5)
	capital = models.IntegerField(default=10)
	match = models.FloatField(default=3)
	seed = models.IntegerField(default=0)

	def start(self, user):
		self.user = user
		self.seed = np.random.randint(1e6)
		np.random.seed(self.seed)  # set random number seed
		if np.random.rand() > 0.5:
			self.userRole = "A"
			self.agentRole = "B"
			name = popB[np.random.randint(len(popB))]
		else:
			self.userRole = "B"
			self.agentRole = "A"
			name = popA[np.random.randint(len(popA))]
		self.agent = Agent.objects.create()
		self.agent.start(name, self.agentRole)
		self.save()
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
	# Status
	currentGame = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="currentGame")
	gamesPlayed = models.IntegerField(default=0)
	doneInformation = models.BooleanField(default=False)
	doneConsent = models.BooleanField(default=False)
	doneSurvey = models.BooleanField(default=False)
	doneTutorial = models.BooleanField(default=False)
	doneRequiredGames = models.BooleanField(default=False)
	doneBonusGames = models.BooleanField(default=False)
	doneCashedOut = models.BooleanField(default=False)
	completionCode = models.CharField(
		max_length=32,
		default=get_random_string(length=32),
		help_text="MTurk Confirmation Code")
	# Survey information
	age = models.IntegerField(
		validators=[MinValueValidator(18), MaxValueValidator(120)],
		null=True, blank=True)
	genderChoices = (
		('', '---'),
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary'))
	gender = models.CharField(
		max_length=300, choices=genderChoices,
		null=True, blank=True)
	income = models.FloatField(
		null=True, blank=True)
	educationChoices = (
		('', '---'),
		('1', 'Primary (middle) school'),
		('2', 'Secondary (high) school'),
		('3', 'Undergraduate degree'),
		('4', 'Graduate degree'),
		('6', 'Other'))
	education = models.CharField(
		max_length=300, choices=educationChoices,
		null=True, blank=True)
	veteran = models.BooleanField(
		null=True, blank=True)
	empathy = models.IntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(10)],
		null=True, blank=True)
	risk = models.IntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(10)],
		null=True, blank=True)
	altruism = models.IntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(10)],
		null=True, blank=True)
	# feedback
	feedback = models.CharField(
		max_length=4200, null=True, blank=True)

	def checkRequirements(self):
		# todo: improved checks for study info, consent, survey, tutorial
		myGame = models.Q(user=self)
		isDone = models.Q(complete=True)
		self.gamesPlayed = Game.objects.filter(myGame and isDone).count()
		self.doneRequiredGames = True if self.gamesPlayed >= 3 else False
		self.doneBonusGames = True if self.gamesPlayed >= 63 else False
		self.save()