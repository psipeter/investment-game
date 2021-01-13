from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.crypto import get_random_string

import uuid
import numpy as np
import random
import pickle

from .agents2 import *
from .utils2 import *


popA = ['Greedy']#, 'TitForTat-A']
popB = ['Greedy']#, 'TitForTat-B']

class Blob(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True, default=str)
	blob = models.BinaryField(null=True)  # for agent class


class Agent(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique agent ID")
	name = models.CharField(max_length=100, blank=True, null=True, default=str)
	created = models.DateTimeField(auto_now_add=True)
	# updateDB = models.BooleanField(default=False)
	blob = models.ForeignKey(Blob, on_delete=models.SET_NULL, null=True, blank=True)
	obj = None  # will store de-pickled blob, the python agent class

	def getObj(self, game):
		name = self.name
		if Blob.objects.filter(name=name).exists():
			# print(f"loaded blob named {name}")
			self.blob = Blob.objects.get(name=name)
			self.save()
			self.obj = pickle.loads(self.blob.blob)
			self.save()
		else:
			# create a new object and blob
			# print(f"creating new blob named {name}")
			if name=='Greedy':
				self.obj = Greedy(None)
			elif name=="Generous":
				self.obj = Generous(None)
			elif name=="TitForTat-A" or name=="TitForTat-B":
				self.obj = TitForTat(None, game.capital)
			# elif saved RL agent
			# load saved npz file
			else:
				raise Exception(f'{name} is not a valid agent class')
			self.blob = Blob.objects.create()
			self.blob.name = name
			self.blob.blob = pickle.dumps(self.obj)
			self.blob.save()
			self.save()			
		self.obj.player = game.agentRole
		self.obj.reset()
		self.save()

	class Meta:
		pass


class Game(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique game ID")
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
	userGives = models.CharField(max_length=300, blank=True, null=True, default=str)
	userKeeps = models.CharField(max_length=300, blank=True, null=True, default=str)
	userTimes = models.CharField(max_length=300, blank=True, null=True, default=str)
	agentGives = models.CharField(max_length=300, blank=True, null=True, default=str)
	agentKeeps = models.CharField(max_length=300, blank=True, null=True, default=str)
	userRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	agentRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	userScore = models.IntegerField(default=0, null=True, blank=True)
	agentScore = models.IntegerField(default=0, null=True, blank=True)
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
		self.agent.name = name
		self.agent.save()
		self.save()
		if self.agentRole == "A":
			self.goAgent(self.capital)
		self.user.currentGame = self
		self.user.save()
		self.save()

	def step(self, userGive, userKeep, userTime):
		self.goHuman(userGive, userKeep, userTime)
		if self.userRole == "A":
			invest = self.movesToArray("user", "give")[-1]
			self.goAgent(self.match*invest)
		elif not self.complete:
			self.goAgent(self.capital)
		self.save()
		self.computeScores()

	def goHuman(self, userGive, userKeep, userTime):
		self.userGives += f"{userGive:d},"
		self.userKeeps += f"{userKeep:d},"
		self.userTimes += f"{userTime:.2f},"
		self.checkComplete()
		self.save()

	def goAgent(self, money):
		self.agent.getObj(self)
		A = "user" if self.userRole=="A" else "agent"
		B = "agent" if self.userRole=="A" else "user"
		history = {
			'aGives': self.movesToArray(A, "give"),
			'aKeeps': self.movesToArray(A, "keep"),
			'bGives': self.movesToArray(B, "give"),
			'bKeeps': self.movesToArray(B, "keep"),
		}
		agentGive, agentKeep = self.agent.obj.act(money, history)
		self.agentGives += f"{agentGive:d},"
		self.agentKeeps += f"{agentKeep:d},"
		self.checkComplete()
		self.save()

	def checkComplete(self):
		userGives = self.movesToArray("user", "give")
		agentGives = self.movesToArray("agent", "give")
		if len(userGives) == self.rounds and len(agentGives) == self.rounds:
			self.complete = True
		if len(userGives) > self.rounds or len(agentGives) > self.rounds:
			raise Exception("Too many moves taken")

	def computeScores(self):
		userGives = self.movesToArray("user", "give")
		userKeeps = self.movesToArray("user", "keep")
		agentGives = self.movesToArray("agent", "give")
		agentKeeps = self.movesToArray("agent", "keep")
		if self.userRole == "A":
			self.userScore = np.sum(userKeeps) + np.sum(agentGives)
			self.agentScore = np.sum(agentKeeps)
		else:
			self.agentScore = np.sum(agentKeeps) + np.sum(userGives)
			self.userScore = np.sum(userKeeps)
		self.save()

	def movesToArray(self, player, action):
		if player == "user":
			if action == "give":
				return np.array(self.userGives.split(',')[:-1]).astype(np.int)
			else:
				return np.array(self.userKeeps.split(',')[:-1]).astype(np.int)
		else:
			if action == "give":
				return np.array(self.agentGives.split(',')[:-1]).astype(np.int)
			else:
				return np.array(self.agentKeeps.split(',')[:-1]).astype(np.int)

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

	class Meta:
		pass