from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.db.models.signals import post_save
from django.dispatch import receiver

import datetime
import uuid
import numpy as np
import random

from .agents import *
from .utils import *
from .plotter import *

def spawnAgent(name, env):
	if name == 'Greedy':
		return Gaussian(mean=0.0, std=0.1, ID="Greedy")
	if name == 'Generous':
		return Gaussian(mean=1.0, std=0.1, ID="Generous")
	if name == 'Accumulator':
		return Accumulator(env)
	if name == 'TitForTat':
		return TitForTat(env)
	if name == "FMQ":
		return FMQ(env, temp=0, decay=0)
	if name == "WoLFPHC":
		return WoLFPHC(env, temp=0, decay=0)
	if name == "PGAAPP":
		return PGAAPP(env)
	if name == "ModelBased":
		return ModelBased(env)
	raise "No Agent Selected"


class Game(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique game ID")
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	agent = models.CharField(max_length=100, default=str)
	userMove = models.IntegerField(null=True, blank=True)
	userMoves = models.CharField(max_length=300, blank=True, null=True, default=str)
	agentMove = models.IntegerField(null=True, blank=True)
	agentMoves = models.CharField(max_length=300, blank=True, null=True, default=str)
	userRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	agentRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	# userMoveList = np.array(self.userMoves.split(',')[:-1]).astype(np.int)
	# agentMoveList = np.array(self.agentMoves.split(',')[:-1]).astype(np.int)
	gameRound = models.IntegerField(default=0)
	complete = models.BooleanField(default=False)
	userScore = models.IntegerField(default=0)
	agentScore = models.IntegerField(default=0)
	env = Env(nIter=5, capital=10, matchFactor=3)
	# agentPool = ["Greedy", "Generous", "Accumulator", "TitForTat"]
	agentPool = ["Accumulator"]
	agentModel = spawnAgent(random.choice(agentPool), env)

	def init(self, request):
		self.user = request.user
		self.agent = self.agentModel.ID
		self.agentModel.loadModel()  # load learned parameters for learning agents
		self.agentModel.reset()
		if np.random.rand() > 0.5:
			self.userRole = "A"
			self.agentRole = "B"
			self.agentModel.setPlayer("B")
		else:
			self.userRole = "B"
			self.agentRole = "A"
			self.agentModel.setPlayer("A")
			invest = self.agentModel.action(self.env.capital) # first move
			self.agentModel.myActions.append(invest)
			self.agentMove = invest
			self.agentMoves += "%s,"%invest
		self.save()

	def step(self, userMove, agentFirst=False):
		self.userMove = userMove
		self.userMoves += "%s,"%userMove
		self.gameRound += 1
		self.complete = True if self.gameRound >= self.env.nIter else False
		if self.userRole == "A":
			invest = int(self.userMove)
			matched = self.env.matchFactor*invest
			reply = self.agentModel.action(matched)
			self.agentModel.myActions.append(reply)
			self.agentModel.otherActions.append(invest)
			self.userScore += int(self.env.capital-invest+reply)
			self.agentScore += int(matched-reply)
			self.agentMove = reply
			self.agentMoves += "%s,"%reply
			self.agentModel.update()
		else:
			invest = int(self.agentMove)
			matched = self.env.matchFactor*invest
			reply = int(self.userMove)
			self.agentScore += int(self.env.capital-invest+reply)
			self.userScore += int(matched-reply)
			if not self.complete:
				self.agentModel.otherActions.append(reply)
				self.agentModel.update()
				newinvest = self.agentModel.action(self.env.capital)
				self.agentModel.myActions.append(newinvest)
				self.agentMove = newinvest
				self.agentMoves += "%s,"%newinvest
			else:
				self.agentModel.reset()
		self.save()


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	age = models.IntegerField(
		validators=[MinValueValidator(18), MaxValueValidator(120)],
		null=True, blank=True)
	genderChoices = (
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary'),
		)
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
		('6', 'Other'),
		)
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


# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()