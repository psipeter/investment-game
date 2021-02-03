import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import time

class Game():
	def __init__(self, A, B, capital, match, turns):
		self.A = A
		self.B = B
		assert self.A.player == "A", "player A not set"
		assert self.B.player == "B", "player B not set"
		self.capital = capital
		self.match = match
		self.turns = turns
		self.history = {
			'aGives': [],
			'aKeeps': [],
			'aRewards': [],
			'aStates': [],
			'bGives': [],
			'bKeeps': [],
			'bRewards': [],
			'bStates': [],
		}
	def play(self):
		self.A.reset()
		self.B.reset()
		for t in range(self.turns):
			aGive, aKeep = self.A.act(self.capital, self.history)
			self.history['aGives'].append(aGive)
			self.history['aKeeps'].append(aKeep)
			self.history['aStates'].append(self.A.state)
			bGive, bKeep = self.B.act(aGive*self.match, self.history)
			self.history['bGives'].append(bGive)
			self.history['bKeeps'].append(bKeep)
			self.history['bStates'].append(self.B.state)
			self.history['aRewards'].append(aKeep+bGive)
			self.history['bRewards'].append(bKeep)
	def historyToDataframe(self, game):
		columns = ('A', 'B', 'game', 'turn', 'aGives', 'aKeeps', 'aRewards', 'aStates', 'bGives', 'bKeeps', 'bRewards', 'bStates')
		dfs = []
		for t in range(self.turns):
			dfs.append(pd.DataFrame([[
				self.A.ID,
				self.B.ID,
				game,
				t,
				self.history['aGives'][t],
				self.history['aKeeps'][t],
				self.history['aRewards'][t],
				self.history['aStates'][t],
				self.history['bGives'][t],
				self.history['bKeeps'][t],
				self.history['bRewards'][t],
				self.history['bStates'][t]
			]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)
		return df


def OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed):
	np.random.seed(seed)
	dfAll = []
	for A in popA:
		for B in popB:
			dfs = []
			for a in range(avg):
				print(f'{A.ID} vs {B.ID}: avg {a}')
				A.restart()
				B.restart()
				for r in range(rounds):
					histories = []
					for g in range(games):
						A.reset()
						B.reset()
						G = Game(A, B, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': A, 'B': B, 'hist': G.history})
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					A.reduceExploration(r)
					B.reduceExploration(r)
			df = pd.concat([df for df in dfs], ignore_index=True)
			dfAll.append(df)
	dfAll = pd.concat([df for df in dfAll], ignore_index=True)
	return dfAll

def ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, name):
	np.random.seed(seed)
	dfs = []
	for a in range(avg):
		print(f'avg {a}')
		for A in popA:
			A.restart()
		for B in popB:
			B.restart()
		for r in range(rounds):
			np.random.shuffle(popA)
			np.random.shuffle(popB)
			histories = []
			for A in popA:
				for B in popB:
					for g in range(games):
						A.reset()
						B.reset()
						G = Game(A, B, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': A, 'B': B, 'hist': G.history})
			# batch learning
			np.random.shuffle(histories)
			for hist in histories:
				hist['A'].learn(hist['hist'])
				hist['B'].learn(hist['hist'])
			for A in popA:
				A.reduceExploration(r)
			for B in popB:
				B.reduceExploration(r)
	dfAll = pd.concat([df for df in dfs], ignore_index=True)
	return dfAll

def plotAll(dfAll, popA, popB, capital, match, rounds, name, endgames=5):
	ylim = ((0, capital*match))
	yticks = (([0, 5, 10, 15, 20, 25, 30]))
	binsAG = np.linspace(0, 1, capital+1)
	binsAR = np.arange(0, match*capital+1, 2)
	binsBG = np.linspace(0, 1, capital+1)
	binsBR = np.arange(0, match*capital+1, 2)
	end = rounds - endgames

	for A in popA:
		AID = A.ID
		dfEnd = dfAll.query('game >= @end & A==@AID')
		gen = dfEnd['aGives'] / (dfEnd['aGives'] + dfEnd['aKeeps']) # plot ignores nan's
		rew = dfEnd['aRewards']
		rew2 = dfEnd['bRewards']
		meanGen = np.mean(gen)
		stdGen = np.std(gen)
		meanRew = np.mean(rew)
		stdRew = np.std(rew)

		fig, ax = plt.subplots()
		sns.histplot(data=gen, ax=ax, stat="probability", bins=binsAG)  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", xticks=((binsAG)), title=f"{AID} (A) Generosity \nMean={meanGen:.2f}, Std={stdGen:.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{AID}A_generosity.pdf")

		fig, ax = plt.subplots()
		sns.histplot(data=rew, ax=ax, stat="probability", bins=binsAR)  
		ax.set(xlabel="Rewards", ylabel="Probability", xticks=((binsAR)), title=f"{AID} (A) Rewards \nMean={meanRew:.2f}, Std={stdRew:.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{AID}A_rewards.pdf")
		plt.close('all')

	for B in popB:
		BID = B.ID
		dfEnd = dfAll.query('game >= @end & B==@BID')
		gen = dfEnd['bGives'] / (dfEnd['bGives'] + dfEnd['bKeeps']) # plot ignores nan's
		rew = dfEnd['bRewards']
		rew2 = dfEnd['aRewards']
		meanGen = np.mean(gen)
		stdGen = np.std(gen)
		meanRew = np.mean(rew)
		stdRew = np.std(rew)

		fig, ax = plt.subplots()
		sns.histplot(data=gen, ax=ax, stat="probability", bins=binsBG)  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", xticks=((binsBG)), title=f"{BID} (B) Generosity \nMean={meanGen:.2f}, Std={stdGen:.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{BID}B_generosity.pdf")

		fig, ax = plt.subplots()
		sns.histplot(data=rew, ax=ax, stat="probability", bins=binsBR)  
		ax.set(xlabel="Rewards", ylabel="Probability", xticks=((binsBR)), title=f"{BID} (B) Rewards \nMean={meanRew:.2f}, Std={stdRew:.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{BID}B_rewards.pdf")
		plt.close('all')

	for A in popA:
		for B in popB:
			AID = A.ID
			BID = B.ID
			df = dfAll.query('A==@AID & B==@BID')
			fig, ax = plt.subplots()
			sns.lineplot(data=df, x='game', y='aRewards', ax=ax, label=f"A: {AID}", ci="sd")
			sns.lineplot(data=df, x='game', y='bRewards', ax=ax, label=f"B: {BID}", ci="sd")
			ax.set(xlabel="Episode", ylabel="Rewards", ylim=ylim, yticks=yticks, title=f"{AID} (A) vs {BID} (B) Learning")
			ax.grid(True, axis='y')
			leg = ax.legend(loc='upper left')
			fig.tight_layout()
			fig.savefig(f"plots/{name}_{AID}A_{BID}B_learning.pdf")
			plt.close('all')

	fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.lineplot(data=dfAll, x='game', y='aRewards', hue="A", ax=ax, ci="sd")
	sns.lineplot(data=dfAll, x='game', y='bRewards', hue="B", ax=ax2, ci="sd")
	ax.set(ylabel="Rewards (A)", ylim=ylim, yticks=yticks, title=f"Overall Learning")
	ax2.set(xlabel="Episode", ylabel="Rewards (B)", ylim=ylim, yticks=yticks, title=f"Overall Learning")
	ax.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg = ax.legend(loc='upper left')
	leg2 = ax.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/{name}_overall_learning.pdf")


def plotForgiveness(dfAll, popA, popB, capital, match, rounds, endgames=5):
	ylim = ((0, capital*match))
	yticks = (([0, 5, 10, 15, 20, 25, 30]))
	end = rounds-endgames
	df = dfAll.query('game >= @end')
	fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.lineplot(data=df, x='A', y='aRewards', hue="B", ax=ax, ci="sd")
	sns.lineplot(data=df, x='A', y='bRewards', hue="B", ax=ax2, ci="sd")
	ax.set(ylabel="Agent Rewards", ylim=ylim, yticks=yticks, title=f"Final Score vs. T4T Forgiveness")
	ax2.set(xlabel="Forgiveness", ylabel="T4T Rewards", ylim=ylim, yticks=yticks)
	ax.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg = ax.legend(loc='upper left')
	leg2 = ax2.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/Forgiveness.pdf")
