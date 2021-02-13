import numpy as np
import random
import pandas as pd

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

def XFriendliness(T4TAs, rlBs, capital, match, turns, avg, rounds, games, seed, dependent, endgames=5):
	end = rounds - endgames
	dfsAll = []
	if dependent == "Forgiveness":
		DV = 'F'
	if dependent == "Punishment":
		DV = 'P'
	if dependent == "Magnitude":
		DV = 'M'
	columns = (DV, 'rO', 'meanA', 'meanB', 'stdA', 'stdB')
	for t4t in T4TAs:
		for rl in rlBs:
			dfs = []
			for a in range(avg):
				print(f'{t4t.ID} F={t4t.F}, P={t4t.P} and {rl.ID} rO={rl.rO}, avg {a}')
				rl.restart()
				for r in range(rounds):
					histories = []
					for g in range(games):
						t4t.reset()
						rl.reset()
						G = Game(t4t, rl, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': t4t, 'B': rl, 'hist': G.history})
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					rl.reduceExploration(r)
			data = pd.concat([df for df in dfs], ignore_index=True)
			dataEnd = data.query("game >= @end")
			meanA = np.mean(dataEnd['aRewards'])
			meanB = np.mean(dataEnd['bRewards'])
			stdA = np.std(dataEnd['aRewards'])
			stdB = np.std(dataEnd['bRewards'])
			if dependent == "Forgiveness":
				DV = t4t.F
			if dependent == "Punishment":
				DV = t4t.P
			if dependent == "Magnitude":
				DV = t4t.F
			dfsAll.append(pd.DataFrame([[DV, rl.rO, meanA, meanB, stdA, stdB]], columns=columns))
	dfFinal = pd.concat([df for df in dfsAll], ignore_index=True)
	return dfFinal



def FriendlinessFriendliness(rlAs, rlBs, capital, match, turns, avg, rounds, games, seed, endgames=5):
	end = rounds - endgames
	dfsAll = []
	columns = ('rOA', 'rOB', 'meanA', 'meanB', 'stdA', 'stdB')
	for rlA in rlAs:
		for rlB in rlBs:
			dfs = []
			for a in range(avg):
				print(f'{rlA.ID} rO={rlA.rO} and {rlB.ID} rO={rlB.rO}, avg {a}')
				rlA.restart()
				rlB.restart()
				for r in range(rounds):
					histories = []
					for g in range(games):
						rlA.reset()
						rlB.reset()
						G = Game(rlA, rlB, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': rlA, 'B': rlB, 'hist': G.history})
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					rlA.reduceExploration(r)
					rlB.reduceExploration(r)
			data = pd.concat([df for df in dfs], ignore_index=True)
			dataEnd = data.query("game >= @end")
			meanA = np.mean(dataEnd['aRewards'])
			meanB = np.mean(dataEnd['bRewards'])
			stdA = np.std(dataEnd['aRewards'])
			stdB = np.std(dataEnd['bRewards'])
			dfsAll.append(pd.DataFrame([[rlA.rO, rlB.rO, meanA, meanB, stdA, stdB]], columns=columns))
	dfFinal = pd.concat([df for df in dfsAll], ignore_index=True)
	return dfFinal
