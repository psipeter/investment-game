from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.core.validators import MaxValueValidator, MinValueValidator
from . import models

class FeedbackForm(forms.Form):
	feedback = forms.CharField(
		max_length=4200,
		label=None,
		widget=forms.Textarea(attrs={
			'rows': 4, 'cols': 40,
			'placeholder': "Your feedback here...questions, comments, suggestions, etc.",
			}))

class LoginForm(forms.Form):
	username = forms.CharField(label="MTurk ID")
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
	username.widget.attrs.update({'placeholder':'MTurk ID'})	
	password.widget.attrs.update({'placeholder':'Password'})	
	username.widget.attrs.update({'autocomplete':'username'})	
	password.widget.attrs.update({'autocomplete':'password'})	
	class Meta:
		model = models.User
		fields = ('username', 'password')

class CreateForm(UserCreationForm):
	username = forms.CharField(label="MTurk ID")
	password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
	password1.widget.attrs.update({'autocomplete':'password'})	
	password2.widget.attrs.update({'autocomplete':'password'})	
	class Meta:
		model = models.User
		fields = ('username', 'password1', 'password2')
		labels = {'username': 'MTurk ID', 'password1': "Enter Password", 'password2': 'Confirm Password'}
		help_texts = {'username': None, 'password1': None, 'password2': None}

class ResetForm(forms.Form):
	username = forms.CharField(label="Mechanical Turk ID")
	password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
	password1.widget.attrs.update({'autocomplete':'password'})	
	password2.widget.attrs.update({'autocomplete':'password'})	
	def clean_username(self):
		username = self.cleaned_data['username']
		if models.User.objects.filter(username=username).exists():
			return self.cleaned_data['username']
		else:
			raise ValidationError("MTurk ID does not exist in database")
	def clean_password2(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_data['password2']
		if password1 == password2:
			return self.cleaned_data['password2']
		else:
			raise ValidationError("Passwords do not match")

class ProfileForm(forms.ModelForm):
	age = forms.IntegerField(min_value=18, max_value=120, required=False)
	genderChoices = (
		('', '---'),
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary'))
	gender = forms.ChoiceField(choices=genderChoices, required=False)
	incomeChoices = (
		('', '---'),
		('1', 'Less than $20,000'),
		('2', '$20,000 - 40,000'),
		('3', '$40,000 - 60,000'),
		('4', '$60,000 - 80,000'),
		('5', '$80,000 - 100,000'),
		('6', 'Greater than $100,000'))
	income = forms.ChoiceField(
		# label="Yearly Household Income (combined before tax income of all working members of the household)",
		label="Yearly Household Income",
		choices=incomeChoices, required=False)
	educationChoices = (
		('', '---'),
		('1', 'Primary (middle) school'),
		('2', 'Secondary (high) school'),
		('3', 'Undergraduate degree'),
		('4', 'Graduate degree'),
		('6', 'Other'))
	education = forms.ChoiceField(choices=educationChoices, required=False)
	veteranChoices = (
		('', '---'),
		('1', 'Yes'),
		('2', 'No'))
	veteran = forms.ChoiceField(
		label="Have you played the Prisoner's Dilemma?",
		choices=veteranChoices,
		required=False)
	empathyLabel = "How easily can you figure out what other people are thinking or feeling during a conversation?"
	empathyHelpText = "1 indicates that you struggle to understand others’ motivations, and 10 indicates that you intuitively understand others’ mental processes."
	riskLabel = "Imagine a coworker approaches you and asks for a $1000 loan, promising to return you the money, plus 20% interest, in a month. How likely are you to trust them and loan them the money?"
	riskHelpText = "1 indicates you wouldn’t give them anything, and 10 indicates you’d given them the full amount."
	altruismLabel = "Imagine you win a million dollars in the lottery. How much do you keep for yourself and how much do you give away to friends, family, and charity?"
	altruismHelpText = "1 indicates you would keep all your winnings, and 10 indicates you would redistribute all your winnings."
	empathy = forms.IntegerField(min_value=1, max_value=10, label=empathyLabel, help_text=empathyHelpText, required=False)
	risk = forms.IntegerField(min_value=1, max_value=10, label=riskLabel, help_text=riskHelpText, required=False)
	altruism = forms.IntegerField(min_value=1, max_value=10, label=altruismLabel, help_text=altruismHelpText, required=False)

	class Meta:
		model = models.User
		fields = ('age', 'gender', 'income', 'education', 'veteran', 'empathy', 'risk', 'altruism')