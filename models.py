from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.conf import settings

import uuid
import numpy as np
import random
import pickle

from .agents import *
from .utils import *

# class BlobStore(models.Model):
# 	key = models.IntegerField(primary_key=True)
# 	value = models.BinaryField()

class Agent(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique agent ID")
	agentType = models.CharField(max_length=100, blank=True, null=True, default=str)
	# agentBlob = models.ForeignKey(BlobStore, on_delete=models.CASCADE, null=True, blank=True)
	agentBlob = models.BinaryField(null=True)
	learning = models.BooleanField(default=False)

	# def __init__(self, *args, **kwargs):
	# 	super(Agent, self).__init__(*args, **kwargs)

	def spawn(self, agentType, env): # todo: integrate into create()
		self.agentType = agentType
		epsilon = 0.01 if self.learning else 0
		temp = 10 if self.learning else 0
		decay = 0.95 if self.learning else 0
		if self.agentType == 'Greedy':
			RL = Gaussian(mean=0.0, std=0.1, ID="Greedy")
		elif self.agentType == 'Generous':
			RL = Gaussian(mean=1.0, std=0.1, ID="Generous")
		elif self.agentType == 'Accumulator':
			RL = Accumulator(env)
		elif self.agentType == 'TitForTat':
			RL = TitForTat(env)
		elif self.agentType == "FMQ":
			RL = FMQ(env, temp=temp, decay=temp, epsilon=epsilon)
		elif self.agentType == "WoLFPHC":
			RL = WoLFPHC(env, temp=temp, decay=decay, epsilon=epsilon)
		elif self.agentType == "PGAAPP":
			RL = PGAAPP(env, temp=temp, decay=decay, epsilon=epsilon)
		elif self.agentType == "ModelBased":
			RL = ModelBased(env, decay=decay, epsilon=epsilon)
		else:
			raise Exception('%s not a valid agentType'%agentType)
		self.serialize(RL)
		self.save()

	def serialize(self, RL):
		# self.agentBlob.key = hash(RL)
		# self.agentBlob.value = pickle.dumps(RL)
		self.agentBlob = pickle.dumps(RL)
		# print(self.agentBlob.key, self.agentBlob.value)
		# self.agentBlob.save()

	def deserialize(self):
		# print(self.agentBlob.value)
		return pickle.loads(self.agentBlob)

	class Meta:
		pass


class Game(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique game ID")
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
	userMove = models.IntegerField(null=True, blank=True)
	agentMove = models.IntegerField(null=True, blank=True)
	userMoves = models.CharField(max_length=300, blank=True, null=True, default=str)
	agentMoves = models.CharField(max_length=300, blank=True, null=True, default=str)
	userRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	agentRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	userScore = models.IntegerField(default=0, null=True, blank=True)
	agentScore = models.IntegerField(default=0, null=True, blank=True)
	complete = models.BooleanField(default=False)
	nIter = models.IntegerField(default=5)
	capital = models.IntegerField(default=10)
	matchFactor = models.FloatField(default=3.0)
	seed = models.IntegerField(default=0)  # np.random.randint(1e10)

	def setMoves(self, player, move):
		if player == "user":
			self.userMove = move
			self.userMoves += "%s,"%move
		else:
			self.agentMove = move
			self.agentMoves += "%s,"%move

	def getMoves(self, string):
		return np.array(string.split(',')[:-1]).astype(np.int)

	def loadRL(self):
		self.RL = self.agent.deserialize()
		self.RL.setPlayer("A" if self.agentRole == "A" else "B")

	def actRL(self, money):
		self.RL.myActions = self.getMoves(self.agentMoves)
		self.RL.otherActions = self.getMoves(self.userMoves)
		if self.RL.player == "A":
			self.RL.rewards = self.capital-self.RL.myActions+self.matchFactor*self.RL.otherActions
		else:
			self.RL.rewards = self.matchFactor*self.RL.otherActions-self.RL.myActions
		self.RL.update()
		return int(self.RL.action(money))

	def getComplete(self):
		userMoves = np.array(self.userMoves.split(',')[:-1]).astype(np.int)
		agentMoves = np.array(self.agentMoves.split(',')[:-1]).astype(np.int)
		if len(self.userMoves) >= self.nIter and len(self.agentMoves) >= self.nIter:
			self.complete = True
		return self.complete

	def start(self, user):
		self.user = user
		np.random.seed(self.seed)  # set random number seed
		env = Env(self.nIter, self.capital, self.matchFactor)
		self.agent = Agent.objects.create()
		self.agent.spawn("Generous", env)  # todo: integrate into create()
		self.save()
		if np.random.rand() > 0.0:  # set to force user to be player A or B
			self.userRole = "A"
			self.agentRole = "B"
		else:
			self.userRole = "B"
			self.agentRole = "A"
			self.loadRL()
			invest = self.actRL(self.capital)
			self.setMoves("agent", invest)
			# self.agent.serialize(self.RL)
		self.user.setCurrentGame(self)
		self.save()

	def step(self, userMove):
		self.setMoves("user", userMove)
		self.getComplete()
		if self.userRole == "A":
			invest = int(self.userMove)
			matched = self.matchFactor*invest
			self.loadRL()
			reply = self.actRL(matched)
			self.userScore += int(self.capital-invest+reply)
			self.agentScore += int(matched-reply)
			self.setMoves("agent", reply)
		else:
			invest = int(self.agentMove)
			matched = self.matchFactor*invest
			reply = int(self.userMove)
			self.agentScore += int(self.env.capital-invest+reply)
			self.userScore += int(matched-reply)
			self.getComplete()
			if not self.getComplete():
				self.loadRL()
				newinvest = self.actRL(self.capital)
				self.setMoves("agent", newinvest)
		# if self.getComplete():
		# 	self.agent.model.reset()
		# 	if self.agent.learning:
		# 		self.agent.model.save(prefix="game/")
		self.save()

	class Meta:
		pass


class User(AbstractUser):
	currentGame = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="currentGame")
	age = models.IntegerField(
		validators=[MinValueValidator(18), MaxValueValidator(120)],
		null=True, blank=True)
	genderChoices = (
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary'))
	gender = models.CharField(
		max_length=300, choices=genderChoices,
		null=True, blank=True)
	income = models.FloatField(
		null=True, blank=True)
	educationChoices = (
		('1', 'Primary (middle) school'),
		('2', 'Secondary (high) school'),
		('3', 'Undergraduate degree'),
		('4', 'Graduate degree'),
		('6', 'Other'))
	education = models.CharField(
		max_length=300, choices=educationChoices,
		null=True, blank=True)
	veteran = models.CharField(
		max_length=300, choices=(('Yes', "Yes"), ("No", "No")),
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

	def setCurrentGame(self, currentGame):
		self.currentGame = currentGame
		self.save()

	class Meta:
		pass