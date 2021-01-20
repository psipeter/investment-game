import numpy as np
from agents import *
from utils import *

capital = 10
match = 3
turns = 10
games = 100
seed = 0

# A = Generous("A")
# A = Greedy("A")
# A = TitForTat("A", capital)
# A = Bandit("A", capital+1)
# A = QLearn("A", capital+1, states=2)
# A = Wolf("A", capital+1, states=2)
# A = Hill("A", capital+1, states=2)
# A = ModelBased("A", capital+1, states=11)

# B = Generous("B")
# B = Greedy("B")
# B = TitForTat("B", capital)
# B = Bandit("B", capital*match+1)
# B = QLearn("B", capital*match+1, states=2)
# B = Wolf("B", capital*match+1, states=2)
# B = ModelBased("B", capital*match+1, states=2)

# games = 10
# agent =	QLearn("A", capital+1, states=2, e0=50, decay=0.95)
# agent.loadArchive(file="data/qlearn.npz")
# agent.epsilon = 0
# opponent = Greedy("B", std=1e-6, epsilon=0)
# df = OneVsOne(agent, opponent, capital, match, turns, games, seed, learn=False)

# df = OneVsOne(A, B, capital, match, turns, games, seed)



avg = 5
rounds = 100
games = 3
turns = 10
player = "B"
actions = capital+1 if player=="A" else capital*match+1
# states = capital if player=="B" else capital*match
states = 5
# seed = 0
seed = np.random.randint(0, 1e6)
popA = [
	QLearn(player, actions, states, decay=0.9),
	Wolf(player, actions, states, dW=2e-1, dL=3e-1, decay=0.9),		Hill(player, actions, states, xi=1, nu=1e-4, decay=0.9),
	ModelBased(player, actions, states, decay=0.9)
	]
popB = [
	Generous(None, std=0.1, epsilon=0.0),
	Greedy(None, std=0.1, epsilon=0.0),
	TitForTat(None, capital, epsilon=0.0),
	]
for agent in popA:
	df = OneVsMany(agent, pop, player, capital, match, turns, avg, rounds, games, seed)
# agent.saveArchive(file="data/qlearn.npz")





rounds = 10
popA = [
	# Generous("A"),
	# Greedy("A"),
	# TitForTat("A", capital),
	# Bandit("A", capital+1),
	# QLearn("A", capital+1, states=2),
	# Wolf("A", capital+1, states=2),
	# Hill("A", capital+1, states=2),
	# ModelBased("A", capital+1, states=2),
	QLearn(player, actions, states, decay=0.9),
	Wolf(player, actions, states, dW=2e-1, dL=3e-1, decay=0.9),
	Hill(player, actions, states, xi=1, nu=1e-4, decay=0.9),

]
popB = [
	Generous("B"),
	Greedy("B"),
	TitForTat("B", capital),
	Bandit("B", capital*match+1),
	QLearn("B", capital*match+1, states=2),
	Wolf("B", capital*match+1, states=2),
	Hill("B", capital*match+1, states=2),
	ModelBased("B", capital*match+1, states=2),
]
# df = ManyVsMany(popA, popB, capital, match, turns, rounds, seed)
