from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from .models import Game, User
from game.forms import LoginForm, CreateForm, ProfileForm, ResetForm, FeedbackForm

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
		else:
			context = {'form':form}
		return render(request, 'login.html', context)

def logout(request):
	auth_logout(request)
	return render(request, 'logout.html')

def reset(request):
	if request.method == 'POST':
		form = ResetForm(request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password1']
			user = User.objects.get(username=username)
			user.set_password(password)
			user.save()
			return redirect('reset_done')
	else:
		form = ResetForm()
	return render(request, 'reset.html', {'form': form})

def reset_done(request):
	return render(request, 'reset_done.html')

def information(request):
	return render(request, "information.html", context={})

def consent_register(request):
	if request.method == 'POST':
		form = CreateForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.save()
			auth_login(request, user)
			user.doneInformation = True
			user.doneConsent = True
			user.save()
			return redirect('home')
	else:
		form = CreateForm()
	return render(request, 'consent_register.html', {'form': form})

@login_required
def tutorial(request):
	request.user.doneTutorial = True  # todo
	request.user.save()
	return render(request, "tutorial.html")

@login_required
def cash_out(request):
	user = request.user
	return render(request, "cash_out.html", {"user": user})

@login_required
def feedback(request):
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			request.user.feedback = request.POST.get('feedback')
			request.user.save()
			return redirect('home')
	else:
		form = FeedbackForm()
	return render(request, "feedback.html", {'form': form})

@login_required
def consent_signed(request):
	return render(request, "consent_signed.html")

@login_required
def survey(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			request.user.doneSurvey = True
			request.user.save()
			return redirect('home')
	else:
		form = ProfileForm(instance=request.user)
	return render(request, 'survey.html', {'form': form})

@login_required
def home(request):
	username = request.user.username
	return redirect('users/%s'%username)

@login_required
def user(request, username):
	if request.user.username != username:
		return redirect('home')  # todo: add warning
	request.user.checkRequirements()
	requiredGames = min(request.user.gamesPlayed, 3)
	bonusGames = max(min(request.user.gamesPlayed, 63)-3, 0)
	context = {
		'user': request.user,
		'path': request.path,
		'requiredGames': requiredGames,
		'bonusGames': bonusGames}
	return render(request, 'home.html', context)

@login_required
def startGame(request):
	# if request.user.currentGame:
	# 	return redirect('continue') # enforce one currentGame
	# todo: special games if request.user.doneRequiredGames is False
	game = Game.objects.create()
	game.start(request.user)
	context = {
		'game': game,
		'userGives': list(game.movesToArray("user", "give")),
		'userKeeps': list(game.movesToArray("user", "keep")),
		'agentGives': list(game.movesToArray("agent", "give")),
		'agentKeeps': list(game.movesToArray("agent", "keep")),
	}
	return render(request, "game.html", context=context)

@login_required
def continueGame(request):
	game = request.user.currentGame
	context = {
		'game': game,
		'userGives': list(game.movesToArray("user", "give")),
		'userKeeps': list(game.movesToArray("user", "keep")),
		'agentGives': list(game.movesToArray("agent", "give")),
		'agentKeeps': list(game.movesToArray("agent", "keep")),
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
		'userGives': str(list(game.movesToArray("user", "give"))),
		'userKeeps': str(list(game.movesToArray("user", "keep"))),
		'userScore': str(game.userScore),
		'agentGives': str(list(game.movesToArray("agent", "give"))),
		'agentKeeps': str(list(game.movesToArray("agent", "keep"))),
		'agentScore': str(game.agentScore),
	}
	if game.complete:
		request.user.currentGame = None
		request.user.save()
		# move learning elsewhere
		if game.complete and game.agent.learn:
			game.agent.learn(game)
		data['complete'] = True
	else:		
		data['complete'] = False
	return JsonResponse(data)