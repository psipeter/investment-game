from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.core.validators import MaxValueValidator, MinValueValidator
from . import models

class UserForm(UserCreationForm):
	username = forms.CharField(label="MTurk ID")
	displayName = forms.CharField(label="Display Name (optional)", required=False)	
	password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
	# todo: validation
	class Meta:
		model = models.User
		fields = ('username', 'displayName', 'password1', 'password2')
		labels = {'username': 'MTurk ID', 'displayName': 'Display Name (optional)', 'password1': "Enter Password", 'password2': 'Confirm Password'}
		help_texts = {'username': None, 'displayName': None, 'password1': None, 'password2': None}


class ProfileForm(forms.ModelForm):
	age = forms.IntegerField(min_value=18, max_value=120, required=False)
	genderChoices = (
		('', '---'),
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary'))
	gender = forms.ChoiceField(choices=genderChoices, required=False)
	income = forms.FloatField(label="Yearly Household Income", required=False)
	educationChoices = (
		('', '---'),
		('1', 'Primary (middle) school'),
		('2', 'Secondary (high) school'),
		('3', 'Undergraduate degree'),
		('4', 'Graduate degree'),
		('6', 'Other'))
	education = forms.ChoiceField(choices=educationChoices, required=False)
	veteran = forms.BooleanField(
		label="Have you played the Prisoner's Dilemma?",
		initial=False,
		required=False)
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
	empathy = forms.IntegerField(min_value=1, max_value=10, help_text=empathyHelpText, required=False)
	risk = forms.IntegerField(min_value=1, max_value=10, help_text=riskHelpText, required=False)
	altruism = forms.IntegerField(min_value=1, max_value=10, help_text=altruismHelpText, required=False)

	class Meta:
		model = models.User
		fields = ('age', 'gender', 'income', 'education', 'veteran', 'empathy', 'risk', 'altruism')