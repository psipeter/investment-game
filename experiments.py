import numpy as np
from agents import *
from utils import *

capital = 10
match = 3
turns = 10

avg = 3
rounds = 8
games = 2
seed = np.random.randint(0, 1e6)

nAA = capital+1
nAB = capital*match+1
rewA = [1, 0, 0, 0]
rewB = [1, 0, 0, 0]
nS = 10

popA = [
	# Generous("A"),
	# Greedy("A"),
	# T4T("A", F=0.0, ID="0%"),
	# T4T("A", F=0.25, ID="25%"),
	# T4T("A", F=0.5, ID="50%"),
	# T4T("A", F=0.75, ID="75%"),
	# T4T("A", F=1.0, ID="100%"),
	Bandit("A", nAA, rew=rewA),
	QLearn("A", nAA, nS, rew=rewA),
	Wolf("A", nAA, nS, rew=rewA),
	Hill("A", nAA, nS, rew=rewA),
	ModelBased("A", nAA, nS, rew=rewA)
	]

popB = [
	# Generous("B"),
	# Greedy("B"),
	# T4T("B", L=0.5, ID="T4TL05"),
	# T4T("B", L=1.0, ID="T4TL10"),
	# T4T("B", L=1.5, ID="T4TL15"),
	Bandit("B", nAB, rew=rewB),
	QLearn("B", nAB, nS, rew=rewB),
	Wolf("B", nAB, nS, rew=rewB),
	Hill("B", nAB, nS, rew=rewB),
	ModelBased("B", nAB, nS, rew=rewB)
	]

# df = OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
# plotAll(df, popA, popB, capital, match, rounds, "1v1")
# plotForgiveness(df, popA, popB, capital, match, rounds)

df = ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, "all")
plotAll(df, popA, popB, capital, match, rounds, "MvM")
