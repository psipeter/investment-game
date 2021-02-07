import numpy as np
from agents import *
from experiments import *
from plotter import *

capital = 10
match = 3
turns = 10

avg = 10
rounds = 100
games = 10
seed = np.random.randint(0, 1e6)

nAA = capital+1
nAB = capital*match+1
nS = 10

FA = 0.5
FB = 0.0
rOA = 0.0
rOB = 0.5

popA = [
	# Generous("A"),
	# Greedy("A"),
	T4T("A", F=FA),
	# Bandit("A", nAA, rO=rOA),
	# QLearn("A", nAA, nS, rO=rOA),
	# Wolf("A", nAA, nS),
	# Hill("A", nAA, nS),
	# ModelBased("A", nAA, nS)
	]

popB = [
	# Generous("B"),
	# Greedy("B"),
	# T4T("B", F=FB, ID=str(FB)),
	# Bandit("B", nAB, rO=rOB),
	QLearn("B", nAB, nS, rO=rOB),
	# Wolf("B", nAB, nS),
	# Hill("B", nAB, nS),
	# ModelBased("B", nAB, nS)
	]

# df = OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
# plotAll(df, popA, popB, capital, match, rounds, "1v1")

# df = ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, "all")
# plotAll(df, popA, popB, capital, match, rounds, "MvM")

# FAs = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
# rOBs = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
# T4TAs = [T4T("A", F=F) for F in FAs]
# rlBs = [ModelBased("B", nAB, nS, rO=rO) for rO in rOBs]
# df = ForgivenessFriendliness(T4TAs, rlBs, capital, match, turns, avg, rounds, games, seed)
# df.to_pickle("data/ModelBasedForgivenessFriendliness.pkl")
# dfLoad = pd.read_pickle("data/ModelBasedForgivenessFriendliness.pkl")
# print(dfLoad)
# plotForgivenessFriendliness(dfLoad, capital, match)


rOAs = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
rOBs = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
rlAs = [Bandit("A", nAA, rO=rO) for rO in rOAs]
# rlBs = [Bandit("B", nAB, rO=rO) for rO in rOBs]
# rlAs = [QLearn("A", nAA, nS, rO=rO) for rO in rOAs]
# rlBs = [QLearn("B", nAB, nS, rO=rO) for rO in rOBs]
# rlAs = [ModelBased("A", nAA, nS, rO=rO) for rO in rOAs]
rlBs = [ModelBased("B", nAB, nS, rO=rO) for rO in rOBs]
df = FriendlinessFriendliness(rlAs, rlBs, capital, match, turns, avg, rounds, games, seed)
df.to_pickle("data/BMFriendlinessFriendliness.pkl")
dfLoad = pd.read_pickle("data/BMFriendlinessFriendliness.pkl")
print(dfLoad)
plotFriendlinessFriendliness(dfLoad, capital, match)

