import numpy as np
from agents import *
from utils import *

capital = 10
match = 3
turns = 10
games = 100
seed = 0

A = Generous("A")
A = Greedy("A")
A = TitForTat("A", capital)
A = Bandit("A", capital+1)
A = QLearn("A", capital+1, states=2)
A = Wolf("A", capital+1, states=2)
A = Hill("A", capital+1, states=2)
A = ModelBased("A", capital+1, states=11)

B = Generous("B")
B = Greedy("B")
B = TitForTat("B", capital)
B = Bandit("B", capital*match+1)
B = QLearn("B", capital*match+1, states=2)
B = Wolf("B", capital*match+1, states=2)
B = ModelBased("B", capital*match+1, states=2)

# df = OneVsOne(A, B, capital, match, turns, games, seed)


rounds = 100
agent =	QLearn("B", capital*match+1, states=2)
role = "A"
pop = [
	Generous(None),
	TitForTat(None, capital),
]
# df = OneVsMany(agent, pop, role, capital, match, turns, rounds, seed)


rounds = 10
popA = [
	Generous("A"),
	Greedy("A"),
	TitForTat("A", capital),
	Bandit("A", capital+1),
	QLearn("A", capital+1, states=2),
	Wolf("A", capital+1, states=2),
	Hill("A", capital+1, states=2),
	ModelBased("A", capital+1, states=2),
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
df = ManyVsMany(popA, popB, capital, match, turns, rounds, seed)
