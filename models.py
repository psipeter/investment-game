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
from .utils import *


# AGENT_POOL = ['Greedy', 'Generous', 'Accumulator', 'TitForTat', 'FMQ', 'WoLFPHC', 'PGAAPP']
AGENT_POOL = ['WoLFPHC']

class Agent(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique agent ID")
	agentType = models.CharField(max_length=100, blank=True, null=True, default=str)
	agentBlob = models.BinaryField(null=True)  # for agent class
	created = models.DateTimeField(auto_now_add=True)
	updateDB = models.BooleanField(default=False)
	# rlBlob = models.BinaryField(null=True)  # for RL matrices
	agentObj = None
	# rlObj = None

	def start(self, agentType, env, player, learning=False): 
		self.agentType = agentType
		epsilon = 0.01 if learning else 0
		temp = 10 if learning else 0
		decay = 0.95 if learning else 0
		if self.agentType == 'Greedy':
			self.agentObj = Gaussian(mean=0.0, std=0.1, ID="Greedy")
		elif self.agentType == 'Generous':
			self.agentObj = Gaussian(mean=1.0, std=0.1, ID="Generous")
		elif self.agentType == 'Accumulator':
			self.agentObj = Accumulator(env)
			self.updateDB = True
		elif self.agentType == 'TitForTat':
			self.agentObj = TitForTat(env)
			self.updateDB = True
		elif self.agentType == "FMQ":
			self.agentObj = FMQ(env, temp=temp, decay=temp, epsilon=epsilon)
		elif self.agentType == "WoLFPHC":
			self.agentObj = WoLFPHC(env, temp=temp, decay=decay, epsilon=epsilon)
		elif self.agentType == "PGAAPP":
			self.agentObj = PGAAPP(env, temp=temp, decay=decay, epsilon=epsilon)
		elif self.agentType == "ModelBased":
			self.agentObj = ModelBased(env, decay=decay, epsilon=epsilon)
		else:
			raise Exception('%s not a valid agentType'%agentType)
		self.agentObj.learning = learning
		self.agentObj.setPlayer(player)
		self.agentObj.load(prefix="game/")  # from disk
		self.saveObj()
		# self.updateRL(fromDisk=True)

	def saveObj(self):
		self.agentBlob = pickle.dumps(self.agentObj)
		self.save()

	def loadObj(self):
		self.agentObj = pickle.loads(self.agentBlob)
		self.save()

	# def saveRL(self, toDisk=False):
	# 	if toDisk:
	# 		self.agentObj.save(prefix="game/")
	# 	self.rlBlob = pickle.dumps(self.rlObj)
	# 	self.save()

	# def loadRL(self):
	# 	self.rlObj = pickle.loads(self.rlBlob)
	# 	self.save()

	def updateAgent(self, game):
		# print('update 1', self.agentObj.state)
		self.loadObj()
		# self.loadRL()
		player = game.agentRole
		myActions = game.getMoves(game.agentMoves)
		otherActions = game.getMoves(game.userMoves)
		if player == "A":
			received = game.capital
			gave = myActions
		else:
			received = game.matchFactor*otherActions[:-1]
			gave = myActions
		rewards = received - gave
		basicDict = {
			'player': player,
			'myActions': myActions,
			'otherActions': otherActions,
			'rewards': rewards,
		}
		# self.agentObj.setData(basicDict, self.rlObj)
		self.agentObj.setData(basicDict)
		self.agentObj.update()  # includes learning
		if self.updateDB:
			self.saveObj()

	# def updateRL(self, fromDisk=False):
	# 	if fromDisk:
	# 		self.agentObj.load(prefix="game/")
	# 	self.rlObj = self.agentObj.getData()
	# 	self.saveRL()

	class Meta:
		pass


class Game(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique game ID")
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
	userMove = models.IntegerField(null=True, blank=True)
	agentMove = models.IntegerField(null=True, blank=True)
	userMoves = models.CharField(max_length=300, blank=True, null=True, default=str)
	userTimes = models.CharField(max_length=300, blank=True, null=True, default=str)
	agentMoves = models.CharField(max_length=300, blank=True, null=True, default=str)
	userRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	agentRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	userScore = models.IntegerField(default=0, null=True, blank=True)
	agentScore = models.IntegerField(default=0, null=True, blank=True)
	complete = models.BooleanField(default=False)
	nIter = models.IntegerField(default=5)
	capital = models.IntegerField(default=10)
	matchFactor = models.FloatField(default=3)
	seed = models.IntegerField(default=0) 

	def start(self, user):
		self.user = user
		self.seed = np.random.randint(1e6)
		np.random.seed(self.seed)  # set random number seed
		if np.random.rand() > 1:
			self.userRole = "A"
			self.agentRole = "B"
		else:
			self.userRole = "B"
			self.agentRole = "A"
		agentType = AGENT_POOL[np.random.randint(len(AGENT_POOL))]
		env = Env(self.nIter, self.capital, self.matchFactor)
		self.agent = Agent.objects.create()
		self.agent.start(agentType, env, self.agentRole)
		self.save()
		if self.agentRole == "A":
			invest = self.goAgent(self.capital)
			self.setMoves("agent", invest)
		self.user.setCurrentGame(self)
		self.save()

	def step(self, userMove, userTime):
		self.setMoves("user", userMove)
		self.setTimes(userTime)
		if self.userRole == "A":
			invest = int(self.userMove)
			matched = self.matchFactor*invest
			reply = self.goAgent(matched)
			self.userScore += int(self.capital-invest+reply)
			self.agentScore += int(matched-reply)
			self.setMoves("agent", reply)
		else:
			invest = int(self.agentMove)
			matched = self.matchFactor*invest
			reply = int(self.userMove)
			self.agentScore += int(self.capital-invest+reply)
			self.userScore += int(matched-reply)
			self.getComplete()
			if not self.getComplete():
				invest = self.goAgent(self.capital)
				self.setMoves("agent", invest)
		self.getComplete()
		self.save()

	def goAgent(self, money):
		self.agent.updateAgent(self)
		# self.agent.updateRL()
		# print('QA', self.agent.agentObj.QA)
		agentMove = int(self.agent.agentObj.action(money))
		return agentMove

	def setMoves(self, player, move):
		if player == "user":
			self.userMove = move
			self.userMoves += "%s,"%move
		else:
			self.agentMove = move
			self.agentMoves += "%s,"%move
		self.save()

	def setTimes(self, time):
		time = int(time.split(".")[0])  # remove digits smaller than ms
		self.userTimes += "%s,"%(time/1000)
		self.save()

	def getMoves(self, string):
		return np.array(string.split(',')[:-1]).astype(np.int)

	def getComplete(self):
		userMoves = np.array(self.userMoves.split(',')[:-1]).astype(np.int)
		agentMoves = np.array(self.agentMoves.split(',')[:-1]).astype(np.int)
		if len(userMoves) == self.nIter and len(agentMoves) == self.nIter:
			self.complete = True
		if len(userMoves) > self.nIter or len(agentMoves) > self.nIter:
			raise Exception("Too many moves taken")
		return self.complete

	class Meta:
		pass


class User(AbstractUser):
	# Status
	currentGame = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="currentGame")
	requiredGames = models.IntegerField(default=0)
	bonusGames = models.IntegerField(default=0)
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

	def setCurrentGame(self, currentGame):
		self.currentGame = currentGame
		if self.requiredGames >= 3:
			self.doneRequiredGames = True
		if self.bonusGames >= 60:
			self.doneBonusGames = True
		self.save()

	def finishGame(self):
		self.currentGame = None
		if not self.doneRequiredGames:
			self.requiredGames += 1
		else:
			self.bonusGames += 1
		if self.requiredGames >= 3:
			self.doneRequiredGames = True
		if self.bonusGames >= 60:
			self.doneBonusGames = True
		self.save()

	class Meta:
		pass