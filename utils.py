import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
try:
	from plotter import *
except:
	from .plotter import *
# from plotter import *
sns.set(context='paper', style='white')


class Env():
	def __init__(self, nIter, capital=10, matchFactor=3):
		self.nIter = nIter
		self.capital = capital
		self.matchFactor = matchFactor

	def matchInvest(self, money):
		return self.matchFactor * money


def playGame(agent1, agent2, env, plot=True):
	players = [agent1.player, agent2.player]
	assert "A" in players and "B" in players
	investor = agent1 if agent1.player=="A" else agent2
	returner = agent1 if agent1.player=="B" else agent2
	for i in range(env.nIter):
		invest = investor.action(env.capital)
		matched = env.matchInvest(invest)
		reply = returner.action(matched)
		investor.myActions.append(invest)
		investor.otherActions.append(reply)
		returner.myActions.append(reply)
		returner.otherActions.append(invest)
		investor.rewards.append(env.capital-invest+reply)
		returner.rewards.append(matched-reply)
		investor.update()
		returner.update()
	if plot:
		plotActions(investor, returner, env)
		plotRewards(investor, returner, env)


def trainQLearning(agent1, agent2, env, nEps, plot=True, report=False):
	rewards1 = np.zeros((nEps))
	rewards2 = np.zeros((nEps))
	for iEp in range(nEps):
		playGame(agent1, agent2, env, plot=False)
		rewards1[iEp] = np.mean(agent1.rewards)
		rewards2[iEp] = np.mean(agent2.rewards)
		agent1.reset()
		agent2.reset()
		if report:
			print('episode %s, %s %.2f, %s %.2f'
				%(iEp, agent1.ID, rewards1[iEp], agent2.ID, rewards2[iEp]))
	if plot:
		plotTraining(rewards1, agent1, rewards2, agent2)
	return rewards1, rewards2


def recovery(agent1, agent2, env, nAvg, nEps):
	agent1.setPlayer("A")
	agent2.setPlayer("B")
	agent1.alpha = 3e-2
	agent2.alpha = 3e-2
	agent1.decay = 0.95
	agent2.decay = 0.95
	rewards1 = np.zeros((nAvg, nEps))
	rewards2 = np.zeros((nAvg, nEps))
	for a in range(nAvg):
		print("condition 1 average %s"%a)
		rewards1[a, :], rewards2[a, :] = trainQLearning(agent1, agent2, env, nEps, plot=False, report=False)
		agent1.fullReset()
		agent2.fullReset()
	rewards3 = np.zeros((nAvg, nEps))
	rewards4 = np.zeros((nAvg, nEps))
	agent1.alpha = 3e-1
	agent2.alpha = 3e-2
	agent1.decay = 0.99
	agent2.decay = 0.95
	for a in range(nAvg):
		print("condition 2 average %s"%a)
		rewards3[a, :], rewards4[a, :] = trainQLearning(agent1, agent2, env, nEps, plot=False, report=False)
		agent1.fullReset()
		agent2.fullReset()
	plotRecovery(agent1, agent2, env, rewards1, rewards2, rewards3, rewards4, agent2.alpha, agent1.alpha)


def performance(agent, pop, env, nAvg, nEps, alphaA=3e-2, alphaB=3e-2, learners=False, plotOther=True):
	# train an invidivual learning agent against each individual nonlearnining agent
	print("agent1 %s"%agent.ID)
	for agent2 in pop:
		print("agent2 %s"%agent2.ID)
		rewardsInvestorA = np.zeros((nAvg, nEps))
		rewardsInvestorB = np.zeros((nAvg, nEps))
		rewardsReturnerA = np.zeros((nAvg, nEps))
		rewardsReturnerB = np.zeros((nAvg, nEps))
		agent.setPlayer("A")
		agent2.setPlayer("B")
		if learners:
			agent.alpha = alphaA
			agent2.alpha = alphaB
		print("A")
		for a in range(nAvg):
			rewardsInvestorA[a, :], rewardsInvestorB[a, :] = trainQLearning(agent, agent2, env, nEps, plot=False, report=False)
			print("average %s, mean reward %s"%(a, np.mean(rewardsInvestorA[a, -10:])))
			agent.fullReset()
			agent2.fullReset()
		print("B")
		agent.setPlayer("B")
		agent2.setPlayer("A")
		if learners:
			agent.alpha = alphaB
			agent2.alpha = alphaA
		for a in range(nAvg):
			rewardsReturnerA[a, :], rewardsReturnerB[a, :] = trainQLearning(agent, agent2, env, nEps, plot=False, report=False)
			print("average %s, mean reward %s"%(a, np.mean(rewardsReturnerA[a, -10:])))
			agent.fullReset()
			agent2.fullReset()
		np.savez("data/%s_vs_%s%s.npz"%(agent.ID, agent2.ID, learners),
			rewardsInvestorA=rewardsInvestorA,
			rewardsInvestorB=rewardsInvestorB,
			rewardsReturnerA=rewardsReturnerA,
			rewardsReturnerB=rewardsReturnerB)
	plotPerformance(agent, pop, env, learners=learners, plotOther=plotOther)


def tournament(pop, env, nAvg, nRounds):
	columns = ("agent1", "agent2", "nAvg", "round", "reward", "player")
	pairs = list(itertools.combinations(pop, 2))
	dfs = []
	for a in range(nAvg):
		print("average %s"%a)
		for r in range(nRounds):
			print('round %s'%r)
			np.random.shuffle(pairs)
			for pair in pairs:
				agent1 = pair[0]
				agent2 = pair[1]
				# print("%s vs %s"%(agent1.ID, agent2.ID))
				agent1.setPlayer("A")
				agent2.setPlayer("B")
				playGame(agent1, agent2, env, plot=False)
				rI, rR = np.mean(agent1.rewards), np.mean(agent2.rewards)
				dfs.append(pd.DataFrame([[agent1.ID, agent2.ID, a, r, rI, "A"]], columns=columns))
				dfs.append(pd.DataFrame([[agent2.ID, agent1.ID, a, r, rR, "B"]], columns=columns))
				agent1.reset()
				agent2.reset()
				agent2.setPlayer("A")
				agent1.setPlayer("B")
				playGame(agent1, agent2, env, plot=False)
				rR, rI = np.mean(agent1.rewards), np.mean(agent2.rewards)
				dfs.append(pd.DataFrame([[agent1.ID, agent2.ID, a, r, rR, "B"]], columns=columns))
				dfs.append(pd.DataFrame([[agent2.ID, agent1.ID, a, r, rI, "A"]], columns=columns))
				agent1.reset()
				agent2.reset()
		for agent in pop:
			agent.saveModel()
			agent.fullReset()
	df = pd.concat([df for df in dfs], ignore_index=True)
	df.to_pickle("data/tournament.pkl")
	plotTournament(pop, df, env)