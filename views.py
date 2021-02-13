from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from .models import Game, User, Feedback
from game.forms import LoginForm, CreateForm, ProfileForm, ResetForm, FeedbackForm
from datetime import datetime
from .parameters import *
# Authentication

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		if User.objects.filter(username=username).exists():
			user = authenticate(username=username, password=password)
			if user: # and user.is_active:
				auth_login(request, user)
				return redirect(reverse('home'))
			else:
				print('password error')
				form.add_error('password', "Password incorrect")
				return render(request, 'login.html', {'form':form})
		else:
			form.add_error('username', "MTurk ID not found")
			return render(request, 'login.html', {'form':form})
	else:
		form = LoginForm()
		if 'next' in request.GET:
			context = {'form':form, 'next': request.GET['next']}
		# todo: added "logged out" message
		# todo: added "password reset" message
		else:
			context = {'form':form}
		return render(request, 'login.html', context)

def logout(request):
	auth_logout(request)
	return redirect('login')
	# return render(request, 'logout.html')

def reset(request):
	if request.method == 'POST':
		form = ResetForm(request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password1']
			user = User.objects.get(username=username)
			user.set_password(password)
			user.save()
			return redirect('login')
	else:
		form = ResetForm()
	return render(request, 'reset.html', {'form': form})


# Account Creation

def information(request):
	return render(request, "information.html")

def consent_register(request):
	# request.user.doneConsent = True
	# request.user.save()
	if request.method == 'POST':
		form = CreateForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.save()
			auth_login(request, user)
			user.doneConsent = datetime.now()
			user.save()
			return redirect('home')
	else:
		form = CreateForm()
	return render(request, 'consent_register.html', {'form': form})

def consent_signed(request):
	return render(request, "consent_signed.html")


# Main Page Links

@login_required
def tutorial(request):
	request.user.doneTutorial = datetime.now()
	request.user.save()
	return render(request, "tutorial.html")

@login_required
def stats(request):
	figures = request.user.makeFigs()
	return render(request, "stats.html", context=figures)

@login_required
def cash_out(request):
	request.user.doneCash = datetime.now()
	request.user.save()
	return render(request, "cash_out.html")

@login_required
def feedback(request):
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			text = request.POST.get('feedback')
			print(text)
			feedback = Feedback.objects.create()
			feedback.text = text
			feedback.save()
			return redirect('home')
	else:
		form = FeedbackForm()
	return render(request, "feedback.html", {'form': form})

@login_required
def survey(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			request.user.doneSurvey = datetime.now()
			request.user.save()
			return redirect('home')
	else:
		form = ProfileForm(instance=request.user)
	return render(request, 'survey.html', {'form': form})

@login_required
def home(request):
	request.user.setProgress()
	context = {
		'username': request.user,
		'path': request.path,
		'N_REQUIRED': N_REQUIRED,
		'N_BONUS': N_BONUS,
		'nRequired': request.user.nRequired,
		'nBonus': request.user.nBonus,
		'doneConsent': request.user.doneConsent,
		'doneSurvey': request.user.doneSurvey,
		'doneTutorial': request.user.doneTutorial,
		'doneRequired': request.user.doneRequired,
		'doneBonus': request.user.doneBonus,
		'doneCash': request.user.doneCash,
		}
	return render(request, 'home.html', context)


# Game Links

@login_required
def startGame(request):
	game = Game.objects.create()
	game.start(request.user)
	context = {
		'game': game,
		'A': game.user if game.userRole == "A" else game.agent.name,
		'B': game.user if game.userRole == "B" else game.agent.name,
		'userGives': list(game.historyToArray("user", "give")),
		'userKeeps': list(game.historyToArray("user", "keep")),
		'userRewards': list(game.historyToArray("user", "reward")),
		'agentGives': list(game.historyToArray("agent", "give")),
		'agentKeeps': list(game.historyToArray("agent", "keep")),
		'agentRewards': list(game.historyToArray("agent", "reward")),
	}
	return render(request, "game.html", context=context)

@login_required
def updateGame(request):
	userGive = int(request.POST.get('userGive'))
	userKeep = int(request.POST.get('userKeep'))
	userTime = float(request.POST.get('userTime'))/1000
	game = request.user.currentGame
	game.step(userGive, userKeep, userTime)
	data = {
		'userGives': str(list(game.historyToArray("user", "give"))),
		'userKeeps': str(list(game.historyToArray("user", "keep"))),
		'userRewards': str(list(game.historyToArray("user", "reward"))),
		'agentGives': str(list(game.historyToArray("agent", "give"))),
		'agentKeeps': str(list(game.historyToArray("agent", "keep"))),
		'agentRewards': str(list(game.historyToArray("agent", "reward"))),
	}
	if game.complete:
		request.user.currentGame = None
		request.user.save()
		data['complete'] = True
		request.user.setProgress()
	else:		
		data['complete'] = False
	# update message to user if they finished the last game in a batch
	if game.agent.name == "tutorial" and request.user.doneTutorial:
		data['doneGames'] = True
		data['message'] = "Tutorial Games Complete!"
	elif game.agent.name == "required" and request.user.doneRequired:
		data['doneGames'] = True
		data['message'] = "Required Games Complete!"
	elif request.user.doneTutorial and request.user.doneRequired and request.user.doneBonus:
		data['doneGames'] = True
		data['message'] = "Bonus Games Complete!"
	else:
		data['doneGames'] = False
		data['message'] = None		
	return JsonResponse(data)