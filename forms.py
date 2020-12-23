from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from . import models

class GameForm(forms.ModelForm):
	userMove = forms.IntegerField(
		label="",
		widget=forms.NumberInput(
			attrs={
				'type':'range',
				'step': '1',
				'min': '0',
				'max': '30',
				'onchange': "updateSend(this.value);"}))
	def clean_userMove(self):
		move = self.cleaned_data['userMove']
		low = 0
		if self.instance.userRole == "A":
			high = self.instance.env.capital
		else:
			high = self.instance.env.matchFactor * self.instance.agentMove 
		if move < low or move > high:
			raise ValidationError('Must enter a number between %s and %s'%(low, high))
		return move
	class Meta:
		model = models.Game
		fields = ('userMove',)

class UserForm(UserCreationForm):
	username = forms.CharField(label="MTurk ID")
	password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
	# todo: validation
	class Meta:
		model = User
		fields = ('username', 'password1', 'password2')
		labels = {'username': 'MTurk ID', 'password1': "Enter Password", 'password2': 'Confirm Password'}
		help_texts = {'username': None, 'password1': None, 'password2': None}

class ProfileForm(forms.ModelForm):
	age = forms.IntegerField(min_value=18, max_value=120)
	genderChoices = (
		('skip', '---'),
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary')
		)
	gender = forms.ChoiceField(choices=genderChoices)
	income = forms.FloatField(label="Yearly Household Income")
	educationChoices = (
		('skip', '---'),
		('1', 'Primary (middle) school'),
		('2', 'Secondary (high) school'),
		('3', 'Undergraduate degree'),
		('4', 'Graduate degree'),
		('6', 'Other'),
		)
	education = forms.ChoiceField(choices=educationChoices)
	veteran = forms.ChoiceField(
		label="Do you have experience playing games similar to the Investment Game?",
		choices=(("No", "No"), ('Yes', "Yes")),
		initial="No",)
	empathyHelpText = "How easily can you figure out what \
		other people are thinking or feeling during a conversation? \
		1 indicates that you struggle to understand others’ motivations, \
		nd 10 indicates that you intuitively understand others’ \
		mental processes."
	riskHelpText = "Imagine a coworker approaches you and \
		asks for a $1000 loan, promising to return you the money, \
		plus 20% interest, in a month. How likely are you to trust \
		them and loan them the money? 1 indicates you wouldn’t give \
		them anything, and 10 indicates you’d given them the full amount."
	altruismHelpText = "Imagine you win a million dollars \
		in the lottery. How much do you keep for yourself and \
		how much do you give away to friends, family, and charity?\
		1 indicates you would keep all your winnings, and 10 \
		indicates you would redistribute all your winnings."
	empathy = forms.IntegerField(min_value=1, max_value=10, help_text=empathyHelpText)
	risk = forms.IntegerField(min_value=1, max_value=10, help_text=riskHelpText)
	altruism = forms.IntegerField(min_value=1, max_value=10, help_text=altruismHelpText)

	class Meta:
		model = models.Profile
		fields = ('age', 'gender', 'income', 'education', 'veteran', 'empathy', 'risk', 'altruism')