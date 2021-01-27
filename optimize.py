import numpy as np
from hyperopt import fmin, tpe, rand, hp, STATUS_OK, Trials, base
# base.have_bson = False
from agents import *
from utils import *

capital = 10
match = 3
turns = 10
avg = 1
rounds = 50
testRounds = 10
games = 3
actions = capital*match+1
evals = 100
seed = np.random.randint(0, 1e6)

# Optimize one agent (B) versus Tit-for-Tat (A)
for agentType in ['Bandit', 'QLearn', 'Wolf', 'Hill', 'ModelBased']:
# agentType = "Bandit"

	P = {
		'capital': capital,
		'match': match,
		'turns': turns,
		'avg': avg,
		'rounds': rounds,
		'testRounds': testRounds,
		'games': games,
		'actions': actions,
		'agentType': agentType,
		'states': hp.quniform('states', 1, capital, 1),
		# 'decay': hp.uniform('decay', 0.5, 0.99),
		'decay': 0.9,
		'gamma': hp.quniform('gamma', 0.1, 0.9, 0.1),
	}
	if P['agentType'] == "Wolf":
		P['dW'] = hp.uniform('dW', 1e-1, 1)
		# P['dL'] = hp.uniform('dL', P['dW'], 1)
	if P['agentType'] == "Hill":
		P['nu'] = hp.uniform('nu', 1e-4, 1e-2)



	def OneVOne(P):
		agentType = P['agentType']
		capital = P['capital']
		match = P['match']
		turns = P['turns']
		avg = P['avg']
		rounds = P['rounds']
		testRounds = P['testRounds']
		games = P['games']
		states = int(P['states'])
		actions = P['actions']
		decay = P['decay']
		gamma = P['gamma']
		seed = np.random.randint(0, 1e6)

		if agentType == "Bandit":
			agent = Bandit("B", actions, decay=decay)
		elif agentType == "QLearn":
			agent = QLearn("B", actions, states, decay=decay, gamma=gamma)
		elif agentType == "Wolf":
			dW = P['dW']
			dL = np.random.uniform(dW, 1)
			agent = Wolf("B", actions, states, decay=decay, gamma=gamma, dW=dW, dL=dL)
		elif agentType == "Hill":
			xi = 1
			nu = P['nu']
			agent = Hill("B", actions, states, decay=decay, gamma=gamma, xi=xi, nu=nu)
		elif agentType == "ModelBased":
			agent = ModelBased("B", actions, states, decay=decay, gamma=gamma)
		else:
			raise "no agent selected"
		popA = [TitForTat("A", capital)]
		popB = [agent]

		df = OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
		rewards = df.query("game >= @testRounds")['bRewards']
		# loss = -np.mean(rewards)
		# loss += np.std(rewards)
		loss = np.sqrt(np.mean(np.square(rewards - capital*match/2*np.ones_like((rewards)))))
		return {
			'loss': loss,
			'rewards': rewards,
			'type': agentType,
			'states': states,
			'decay': decay,
			'gamma': gamma,
			'status': STATUS_OK}

	trials = Trials()
	fmin(OneVOne,
		rstate=np.random.RandomState(seed=seed),
		space=P,
		# algo=tpe.suggest,
		algo=rand.suggest,
		max_evals=evals,
		trials=trials)
	idx = np.argmin(trials.losses())
	best = trials.trials[idx]
	params = best['result']
	rewards = params['rewards']
	fig, ax = plt.subplots()
	sns.histplot(rewards, ax=ax, bins=np.arange(0, capital*match+1))
	ax.set(xlabel="rewards (B)",
		title=f"{params['type']}, mean={int(np.mean(params['rewards']))}, std={int(np.std(params['rewards']))}")
	fig.savefig(f"plots/optimize_OneVOne_{agentType}.pdf")
	print(params)



# Optimize one agent (B) vs many agents, including Tit-for-Tat (A)
P['popSize'] = 5
# P['statesA'] = 5
P['statesA'] = hp.quniform('statesA', 1, 10, 1)


def OneVMany(P):
	agentType = P['agentType']
	capital = P['capital']
	match = P['match']
	turns = P['turns']
	avg = P['avg']
	rounds = P['rounds']
	testRounds = P['testRounds']
	games = P['games']
	states = int(P['states'])
	statesA = int(P['statesA'])
	actions = P['actions']
	popSize = P['popSize']
	decay = P['decay']
	gamma = P['gamma']
	seed = np.random.randint(0, 1e6)

	popA = [TitForTat("A", capital)]
	agentIdx = np.random.randint(0, 8, popSize)
	for idx in agentIdx:
		if idx==0:
			popA.append(Generous("A"))
		elif idx==1:
			popA.append(Greedy("A"))
		elif idx==2:
			popA.append(TitForTat("A", capital))
		elif idx==3:
			popA.append(Bandit("A", actions=capital+1))
		elif idx==4:
			popA.append(QLearn("A", actions=capital+1, states=statesA))
		elif idx==5:
			agent = Wolf("A", actions=capital+1, states=statesA)
		elif idx==6:
			popA.append(Hill("A", actions=capital+1, states=statesA))
		elif idx==7:
			popA.append(ModelBased("A", actions=capital+1, states=statesA))

	if agentType == "Bandit":
		agent = Bandit("B", actions, decay=decay)
	elif agentType == "QLearn":
		agent = QLearn("B", actions, states, decay=decay, gamma=gamma)
	elif agentType == "Wolf":
		dW = P['dW']
		dL = np.random.uniform(dW, 1)
		agent = Wolf("B", actions, states, decay=decay, gamma=gamma, dW=dW, dL=dL)
	elif agentType == "Hill":
		agent = Hill("B", actions, states, decay=decay, gamma=gamma, xi=1, nu=P['nu']),
	elif agentType == "ModelBased":
		agent = ModelBased("B", actions, states, decay=decay, gamma=gamma)
	popB = [agent]

	df = OneVsMany(popA, popB, "A", capital, match, turns, avg, rounds, games, seed)
	rewards = df.query("game>=@testRounds")['bRewards']
	rewardsT4T = df.query("game>=@testRounds & A=='TitForTat'")['bRewards']
	loss = -np.mean(rewards)
	# loss += np.std(rewards)
	return {
		'loss': loss,
		'rewards': rewards,
		'rewardsT4T': rewardsT4T,
		'type': agentType,
		'agentIdx': agentIdx,
		'states': states,
		'decay': decay,
		'gamma': gamma,
		'status': STATUS_OK}

# trials = Trials()
# fmin(OneVMany,
# 	rstate=np.random.RandomState(seed=seed),
# 	space=P,
# 	algo=tpe.suggest,
# 	max_evals=evals,
# 	trials=trials)
# idx = np.argmin(trials.losses())
# best = trials.trials[idx]
# params = best['result']
# # rewards = params['rewards']
# rewards = params['rewardsT4T']
# fig, ax = plt.subplots()
# sns.histplot(rewards, ax=ax, bins=np.arange(0, capital*match+1))
# ax.set(xlabel="rewards (B)",
# 	title=f"{params['type']}, mean={int(np.mean(params['rewards']))}, std={int(np.std(params['rewards']))}")
# fig.savefig("plots/optimize_OneVMany.pdf")
# print(params)