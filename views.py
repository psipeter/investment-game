from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Game, User
from game.forms import UserForm, ProfileForm, GameForm

def information(request):
	return render(request, "information.html", context={})

def consent_register(request):
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('home')
	else:
		form = UserForm()
	return render(request, 'consent_register.html', {'form': form})

@login_required
def consent_signed(request):
	return render(request, "consent_signed.html")

@login_required
def survey(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
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
	myGames = Game.objects.filter(user=request.user).count()
	context = {'user': request.user, 'myGames': myGames, 'path': request.path}
	return render(request, 'home.html', context)

@login_required
def startGame(request):
	game = Game()
	game.start(request.user)
	form = GameForm(instance=game)
	context = {'game': game, 'form': form}
	return render(request, "game.html", context=context)

@login_required
def updateGame(request):
	userMove = request.POST.get('userMove')
	game = request.user.currentGame
	game.step(userMove)
	data = {
		'userMove': game.userMove,
		'userMoves': game.userMoves,
		'agentMove': game.agentMove,
		'agentMoves': game.agentMoves,
	}
	return JsonResponse(data)