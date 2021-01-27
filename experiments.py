import numpy as np
from agents import *
from utils import *

capital = 10
match = 3
turns = 10

avg = 5
rounds = 50
games = 3

actionsA = capital+1
actionsB = capital*match+1
states = 5
rep = "other"

seed = np.random.randint(0, 1e6)

popA = [
	# Generous("A"),
	# Greedy("A"),
	Accumulator("A", capital),
	TitForTat("A", capital),
	# Bandit("A", actionsA),
	QLearn("A", actionsA, states, rep=rep),
	# Wolf("A", actionsA, states, rep=rep),
	# Hill("A", actionsA, states, rep=rep),
	# ModelBased("A", actionsA, states, rep=rep)
	]
popB = [
	# Generous("B"),
	# Greedy("B"),
	Accumulator("B", capital),
	TitForTat("B", capital),
	# Bandit("B", actionsB),
	QLearn("B", actionsB, states, rep=rep),
	# Wolf("B", actionsB, states, rep=rep),
	# Hill("B", actionsB, states, rep=rep),
	# ModelBased("B", actionsB, states, rep=rep)
	]

# OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
# OneVsMany(popA, popB, "B", capital, match, turns, avg, rounds, games, seed)
ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, "all")