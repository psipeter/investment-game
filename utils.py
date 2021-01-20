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
			'bGives': [],
			'bKeeps': [],
			'bRewards': [],
		}
	def play(self):
		for t in range(self.turns):
			aGive, aKeep = self.A.act(self.capital, self.history)
			self.history['aGives'].append(aGive)
			self.history['aKeeps'].append(aKeep)
			bGive, bKeep = self.B.act(aGive*self.match, self.history)
			self.history['bGives'].append(bGive)
			self.history['bKeeps'].append(bKeep)
			self.history['aRewards'].append(aKeep+bGive)
			self.history['bRewards'].append(bKeep)
		self.A.reset()
		self.B.reset()
	def historyToDataframe(self, game):
		columns = ('A', 'B', 'game', 'turn', 'aGives', 'aKeeps', 'aRewards', 'bGives', 'bKeeps', 'bRewards')
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
				self.history['bGives'][t],
				self.history['bKeeps'][t],
				self.history['bRewards'][t]
			]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)
		return df


def OneVsOne(A, B, capital, match, turns, games, seed, learn=True):
	dfs = []
	for g in range(games):
		np.random.seed(seed+g)
		G = Game(A, B, capital, match, turns)
		G.play()
		dfs.append(G.historyToDataframe(g))
		if learn:
			A.learn(G.history)
			B.learn(G.history)
			A.reduceExploration(g)
			B.reduceExploration(g)
	df = pd.concat([df for df in dfs], ignore_index=True)
	ylim = ((0, capital*match))
	fig, ax = plt.subplots()
	sns.lineplot(data=df, x='game', y='aRewards', ax=ax, label="A: "+A.ID)
	sns.lineplot(data=df, x='game', y='bRewards', ax=ax, label="B: "+B.ID)
	ax.set(xlabel="round", ylim=ylim, yticks=(([0, 5, 10, 15, 20, 25, 30])), title=f"{A.ID} vs {B.ID}")
	ax.grid(True, axis='y')
	leg = ax.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/{A.ID}_vs_{B.ID}.pdf")
	return df

def OneVsMany(agent, pop, player, capital, match, turns, avg, rounds, games, seed):
	dfs = []
	for a in range(avg):
		print(f'average {a}')
		agent.restart()
		for other in pop:
			other.restart()
		for r in range(rounds):
			# print(f'round {r}')
			np.random.shuffle(pop)
			histories = []
			for other in pop:
				if player == "A":
					A = agent
					B = other
				else:
					A = other
					B = agent
				A.player = "A"
				B.player = "B"
				for g in range(games):
					A.reset()
					B.reset()
					np.random.seed(seed)
					G = Game(A, B, capital, match, turns)
					G.play()
					dfs.append(G.historyToDataframe(r))
					histories.append({'A': A, 'B': B, 'hist': G.history})
					seed += 1
			# batch learning
			np.random.shuffle(histories)
			for hist in histories:
				# start = time.time()
				hist['A'].learn(hist['hist'])
				hist['B'].learn(hist['hist'])
				# end = time.time()
				# print(f"learning time: {end-start} seconds")
			agent.reduceExploration(r)
			for other in pop:
				other.reduceExploration(r)
		# print(np.argmax(agent.Q, axis=1))
		# print(agent.nSA)

	df = pd.concat([df for df in dfs], ignore_index=True)
	# df.to_pickle(f"plots/{agent.ID}_vsMany.pkl")
	# agent.save()
	ylim = ((0, capital*match))
	hue_order = [agent.ID for agent in pop]
	fig, ax = plt.subplots()
	player2 = "B" if player == "A" else "A"
	if player == "A":
		sns.lineplot(data=df, x="game", y="aRewards", hue=player2, ax=ax, hue_order=hue_order)
	else:
		sns.lineplot(data=df, x="game", y="bRewards", hue=player2, ax=ax, hue_order=hue_order)
	ax.set(xlabel="round", ylim=ylim, yticks=(([0, 5, 10, 15, 20, 25, 30])), title=f"{player}: {agent.ID}")
	ax.grid(True, axis='y')
	leg = ax.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/{agent.ID}_{player}_vs_Many.pdf")
	return df

def ManyVsMany(popA, popB, capital, match, turns, rounds, seed):
	dfs = []
	g = 0
	for r in range(rounds):
		print(f'round {r}')
		np.random.shuffle(popA)
		histories = []
		for A in popA:
			np.random.shuffle(popB)
			for B in popB:
				A.reset()
				B.reset()
				np.random.seed(seed+g)
				G = Game(A, B, capital, match, turns)
				G.play()
				dfs.append(G.historyToDataframe(g))
				histories.append({'A': A, 'B': B, 'hist': G.history})
				g += 1
		# batch learning
		np.random.shuffle(histories)
		for hist in histories:
			hist['A'].learn(hist['hist'])
			hist['B'].learn(hist['hist'])
		for A in popA:
			A.reduceExploration(r)
		for B in popB:
			B.reduceExploration(r)
	df = pd.concat([df for df in dfs], ignore_index=True)
	# df.to_pickle("data/tournament.pkl")
	ylim = ((0, capital*match))
	fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.lineplot(data=df, x="game", y="aRewards", hue="B", ax=ax1)
	sns.lineplot(data=df, x="game", y="bRewards", hue="A", ax=ax2)
	ax1.set(xlabel="round", ylim=ylim, yticks=(([0, 5, 10, 15, 20, 25, 30])), title="A")
	ax2.set(xlabel="round", ylim=ylim, yticks=(([0, 5, 10, 15, 20, 25, 30])), title="B")
	ax1.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg1 = ax1.legend(loc='upper left')
	leg2 = ax2.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/Many_vs_Many.pdf")
	return df
