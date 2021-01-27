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


def OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed, learn=True, endgames=10):
	np.random.seed(seed)
	ylim = ((0, capital*match))
	yticks = (([0, 5, 10, 15, 20, 25, 30]))
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
					if learn:
						np.random.shuffle(histories)
						for hist in histories:
							hist['A'].learn(hist['hist'])
							hist['B'].learn(hist['hist'])
						A.reduceExploration(r)
						B.reduceExploration(r)
			df = pd.concat([df for df in dfs], ignore_index=True)
			dfAll.append(df)
			dfEnd = df.query('game >= @endgames')
			ratiosA = dfEnd['aGives'] / (dfEnd['aGives'] + dfEnd['aKeeps']) # plot ignores nan's
			ratiosB = dfEnd['bGives'] / (dfEnd['bGives'] + dfEnd['bKeeps']) # plot ignores nan's
			fig, ax = plt.subplots()
			sns.lineplot(data=df, x='game', y='aRewards', ax=ax, label=f"A: {A.ID}", ci="sd")
			sns.lineplot(data=df, x='game', y='bRewards', ax=ax, label=f"B: {B.ID}", ci="sd")
			ax.set(xlabel="round", ylabel="mean rewards", ylim=ylim, yticks=yticks, title=f"{A.ID} vs {B.ID}")
			ax.grid(True, axis='y')
			leg = ax.legend(loc='upper left')
			fig.tight_layout()
			fig.savefig(f"plots/1v1_{A.ID}A_{B.ID}B_learn.pdf")
			fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2)
			sns.histplot(data=ratiosA, ax=ax, stat="probability", bins=np.linspace(0, 1, 10))  
			sns.histplot(data=ratiosB, ax=ax2, stat="probability", bins=np.linspace(0, 1, 10))  
			ax.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{A.ID} (A) Generosity")
			ax2.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{B.ID} (B) Generosity")
			ax.grid(True, axis='y')
			fig.tight_layout()
			fig.savefig(f"plots/1v1_{A.ID}A_{B.ID}B_dist.pdf")
			plt.close('all')
	dfAll = pd.concat([df for df in dfAll], ignore_index=True)
	for A in popA:
		AID = A.ID
		dfA = dfAll.query('A==@AID')
		fig, ax = plt.subplots()
		sns.lineplot(data=dfA, x='game', y='aRewards', ax=ax, label=f"A: {AID}", ci="sd")
		sns.lineplot(data=dfA, x='game', y='bRewards', ax=ax, label="mean B", ci="sd")
		ax.set(xlabel="round", ylabel="mean rewards", ylim=ylim, yticks=yticks, title=f"mean {A.ID} (A)")
		ax.grid(True, axis='y')
		leg = ax.legend(loc='upper left')
		fig.tight_layout()
		fig.savefig(f"plots/1v1_{AID}A_learn.pdf")
		dfEnd = dfAll.query('game >= @endgames & A==@AID')
		ratiosA = dfEnd['aGives'] / (dfEnd['aGives'] + dfEnd['aKeeps']) # plot ignores nan's
		fig, ax = plt.subplots()
		sns.histplot(data=ratiosA, ax=ax, stat="probability", bins=np.linspace(0, 1, 10))  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{A.ID} (A) Generosity")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/1v1_{A.ID}A_dist.pdf")
		plt.close('all')
	for B in popB:
		BID = B.ID
		dfB = dfAll.query('B==@BID')
		fig, ax = plt.subplots()
		sns.lineplot(data=dfB, x='game', y='aRewards', ax=ax, label=f"mean A", ci="sd")
		sns.lineplot(data=dfB, x='game', y='bRewards', ax=ax, label=f"B: {BID}", ci="sd")
		ax.set(xlabel="round", ylabel="mean rewards", ylim=ylim, yticks=yticks, title=f"mean {BID} (B)")
		ax.grid(True, axis='y')
		leg = ax.legend(loc='upper left')
		fig.tight_layout()
		fig.savefig(f"plots/1v1_{BID}B_learn.pdf")
		dfEnd = dfAll.query('game >= @endgames & B==@BID')
		ratiosB = dfEnd['bGives'] / (dfEnd['bGives'] + dfEnd['bKeeps']) # plot ignores nan's
		fig, ax = plt.subplots()
		sns.histplot(data=ratiosB, ax=ax, stat="probability", bins=np.linspace(0, 1, 10))  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{BID} (B) Generosity")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/1v1_{BID}B_dist.pdf")
		plt.close('all')
	return dfAll

def OneVsMany(popA, popB, player, capital, match, turns, avg, rounds, games, seed, learn=True):
	player2 = "B" if player == "A" else "A"
	np.random.seed(seed)
	ylim = ((0, capital*match))
	yticks = (([0, 5, 10, 15, 20, 25, 30]))
	hue_order = [agentB.ID for agentB in popB]
	dfAll = []
	for agentA in popA:
		dfs = []
		for a in range(avg):
			print(f'{agentA.ID}: avg {a}')
			agentA.restart()
			for agentB in popB:
				agentB.restart()
			for r in range(rounds):
				histories = []
				for agentB in popB:
					A = agentA if player == "A" else agentB
					B = agentB if player == "A" else agentA
					for g in range(games):
						A.reset()
						B.reset()
						G = Game(A, B, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': A, 'B': B, 'hist': G.history})
				if learn:
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					agentA.reduceExploration(r)
					agentB.reduceExploration(r)
		df = pd.concat([df for df in dfs], ignore_index=True)
		dfAll.append(df)
		fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
		if player == "A":
			sns.lineplot(data=df, x="game", y="aRewards", hue=player2, ax=ax, hue_order=hue_order, ci="sd")
			sns.lineplot(data=df, x="game", y="bRewards", hue=player2, ax=ax2, linestyle="--", hue_order=hue_order, ci="sd")
			ax.set(ylabel=f"{agentA.ID} (A) rewards", ylim=ylim, yticks=yticks, title=f"{A.ID} ({player}) vs Many ({player2})")
			ax2.set(xlabel="round", ylabel=f"Opponent (B) rewards", ylim=ylim, yticks=yticks)
		else:
			sns.lineplot(data=df, x="game", y="aRewards", hue=player2, ax=ax, linestyle="--", hue_order=hue_order, ci="sd")
			sns.lineplot(data=df, x="game", y="bRewards", hue=player2, ax=ax2, hue_order=hue_order, ci="sd")
			ax.set(ylabel=f"Opponent (A) rewards", ylim=ylim, yticks=yticks, title=f"{A.ID} ({player}) vs Many ({player2})")
			ax2.set(xlabel="round", ylabel=f"{agentA.ID} (B) rewards", ylim=ylim, yticks=yticks)
		ax.grid(True, axis='y')
		ax2.grid(True, axis='y')
		leg = ax.legend(loc='upper left')
		leg2 = ax2.legend(loc='upper left')
		fig.tight_layout()
		fig.savefig(f"plots/1vM_{agentA.ID}{player}_learn.pdf")
		plt.close('all')

	dfAll = pd.concat([df for df in dfAll], ignore_index=True)	
	return dfAll

def ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, name, endgames=10):
	np.random.seed(seed)
	# ylim = ((0, capital*match))
	ylim = ((0, 20))
	# yticks = (([0, 5, 10, 15, 20, 25, 30]))
	yticks = (([0, 5, 10, 15, 20]))
	hue_orderA = [A.ID for A in popA]
	hue_orderB = [B.ID for B in popB]
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
	df = pd.concat([df for df in dfs], ignore_index=True)

	fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.lineplot(data=df, x="game", y="aRewards", hue="A", hue_order=hue_orderA, ax=ax1)#, ci="sd")
	sns.lineplot(data=df, x="game", y="bRewards", hue="B", hue_order=hue_orderB, ax=ax2)#, ci="sd")
	ax1.set(xlabel="round", ylabel="A reward", ylim=ylim, yticks=yticks, title="A")
	ax2.set(xlabel="round", ylabel="B reward", ylim=ylim, yticks=yticks, title="B")
	ax1.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg1 = ax1.legend(loc='upper left')
	leg2 = ax2.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/MvM_{name}.pdf")

	for agentA in popA:
		AID = agentA.ID
		dfA = df.query("A == @AID")
		fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
		sns.lineplot(data=dfA, x="game", y="aRewards", hue="B", ax=ax, hue_order=hue_orderB, ci="sd")
		sns.lineplot(data=dfA, x="game", y="bRewards", hue="B", ax=ax2, linestyle="--", hue_order=hue_orderB, ci="sd")
		ax.set(ylabel=f"{AID} (A) rewards", ylim=ylim, yticks=yticks, title=f"{AID} (A) Breakdown")
		ax2.set(xlabel="round", ylabel=f"Opponent (B) rewards", ylim=ylim, yticks=yticks)
		ax.grid(True, axis='y')
		ax2.grid(True, axis='y')
		leg = ax.legend(loc='upper left')
		leg2 = ax2.legend(loc='upper left')
		fig.tight_layout()
		fig.savefig(f"plots/MvM_{AID}A_learn.pdf")
		plt.close('all')		
		dfEnd = df.query('game>=@endgames & A==@AID')
		ratios = dfEnd['aGives'] / (dfEnd['aGives'] + dfEnd['aKeeps']) # plot ignores nan's
		fig, ax = plt.subplots()
		sns.histplot(data=ratios, ax=ax, stat="probability", bins=np.linspace(0, 1, 10))  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{AID} (A) Generosity")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/MvM_{AID}A_dist.pdf")
		plt.close('all')
		for agentB in popB:
			BID = agentB.ID
			dfABEnd = df.query('game>=@endgames & A==@AID & B==@BID')
			ratiosA = dfABEnd['aGives'] / (dfABEnd['aGives'] + dfABEnd['aKeeps']) # plot ignores nan's
			ratiosB = dfABEnd['bGives'] / (dfABEnd['bGives'] + dfABEnd['bKeeps']) # plot ignores nan's
			fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2)
			sns.histplot(data=ratiosA, ax=ax, stat="probability", bins=np.linspace(0, 1, 10))  
			sns.histplot(data=ratiosB, ax=ax2, stat="probability", bins=np.linspace(0, 1, 10))  
			ax.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{AID} (A) Generosity")
			ax2.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{BID} (B) Generosity")
			ax.grid(True, axis='y')
			fig.tight_layout()
			fig.savefig(f"plots/MvM_{AID}A_{BID}B_dist.pdf")
			plt.close('all')


	for agentB in popB:
		BID = agentB.ID
		dfB = df.query("B == @BID")
		fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
		sns.lineplot(data=dfB, x="game", y="aRewards", hue="A", ax=ax, linestyle="--", hue_order=hue_orderA, ci="sd")
		sns.lineplot(data=dfB, x="game", y="bRewards", hue="A", ax=ax2, hue_order=hue_orderA, ci="sd")
		ax.set(ylabel=f"Opponent (A) rewards", ylim=ylim, yticks=yticks, title=f"{BID} (B) Breakdown")
		ax2.set(xlabel="round", ylabel=f"{BID} (B) rewards", ylim=ylim, yticks=yticks)
		ax.grid(True, axis='y')
		ax2.grid(True, axis='y')
		leg = ax.legend(loc='upper left')
		leg2 = ax2.legend(loc='upper left')
		fig.tight_layout()
		fig.savefig(f"plots/MvM_{BID}B_learn.pdf")
		plt.close('all')
		dfEnd = df.query('game>=@endgames & B==@BID')
		ratios = dfEnd['bGives'] / (dfEnd['bGives'] + dfEnd['bKeeps']) # plot ignores nan's
		fig, ax = plt.subplots()
		sns.histplot(data=ratios, ax=ax, stat="probability", bins=np.linspace(0, 1, 10))  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", title=f"{BID} (B) Generosity")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/MvM_{BID}B_dist.pdf")
		plt.close('all')
