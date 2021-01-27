import numpy as np
from scipy.special import softmax
import random

class AgentBase():
	def act(self, money, history):
		pass
	def getState(self, history, t):
		pass
	def update(self, history):
		pass
	def learn(self, history):
		pass
	def reset(self):
		pass
	def restart(self):
		pass
	def reduceExploration(self, i):
		pass
	def replayHistory(self, history):
		pass

class HardcodedAgent(AgentBase):
	def act(self, money, history):
		self.update(history)
		if money == 0:
			a = 0
		elif np.random.rand() < self.epsilon:
			a = np.random.randint(0, money+1)
		else:
			a = money * self.state
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		# print('hard', give)
		return give, keep

class Generous(HardcodedAgent):
	def __init__(self, player, mean=1.0, std=0.05, epsilon=0, ID="Generous"):
		self.player = player
		self.ID = ID
		self.mean = mean
		self.std = std
		self.epsilon = epsilon
		self.state = 0
	def update(self, history):
		self.state = np.random.normal(self.mean, self.std)

class Greedy(HardcodedAgent):
	def __init__(self, player, mean=0.0, std=0.05, epsilon=0, ID="Greedy"):
		self.player = player
		self.ID = ID
		self.mean = mean
		self.std = std
		self.epsilon = epsilon
		self.state = 1
	def update(self, history):
		self.state = np.random.normal(self.mean, self.std)

class Accumulator(HardcodedAgent):
	def __init__(self, player, capital, alpha=2e-1, epsilon=0, ID="Accumulator"):
		self.player = player
		self.ID = ID
		self.capital = capital
		self.alpha = alpha
		self.epsilon = epsilon
		self.state = 1.0 if self.player=="A" else 0.5
		self.maxGive = 1.0 if self.player=="A" else 0.5
	def update(self, history):
		if len(history['aGives'])==0 or len(history['bGives'])==0:
			return
		if self.player == "A":
			if history['bGives'][-1] > history['aGives'][-1]:
				self.state += self.alpha
			elif history['bGives'][-1] < history['aGives'][-1]:
				self.state -= self.alpha
			self.state = np.clip(self.state, 0, self.maxGive)
		elif self.player == "B":
			if history['aGives'][-1] == self.capital:
				self.state += self.alpha
			else:
				self.state -= self.alpha
			self.state = np.clip(self.state, 0, self.maxGive)
		else:
			raise "player not set"
	def replayHistory(self, history):
		steps = min(len(history['aGives']), len(history['bGives']))
		for t in range(steps):
			historySlice = {
				'aGives': history['aGives'][:t+1],
				'aKeeps': history['aKeeps'][:t+1],
				'bGives': history['bGives'][:t+1],
				'bKeeps': history['bKeeps'][:t+1],
			}
			self.update(historySlice)
	def reset(self):
		self.state = 1.0 if self.player=="A" else 0.5
		self.maxGive = 1.0 if self.player=="A" else 0.5

class TitForTat(HardcodedAgent):
	def __init__(self, player, capital, epsilon=0, ID="TitForTat"):
		self.player = player
		self.ID = ID
		self.capital = capital
		self.epsilon = epsilon
		self.state = 1 if self.player=="A" else 0.5
	def update(self, history):
		if len(history['aGives'])==0 or len(history['bGives'])==0:
			return
		if self.player == "A":
			# if A gave nothing last turn:
			if history['aGives'][-1] == 0:
				# self.state = 0  # continue punishing
				self.state = 0.1  # chance for redemption
				# self.state = np.random.rand()  # random action
			# if A gave something last turn
			else:
				# happy if B gave more than B kept
				if history['bKeeps'][-1] == 0:
					self.state = 1  # avoid div by zero
				else:
					self.state =  history['bGives'][-1] / history['bKeeps'][-1]
			self.state = np.clip(self.state, 0, 1)
		elif self.player == "B":
			# happy if A gave 100% of capital
			self.state = 0.5 * history['aGives'][-1] / self.capital
			self.state = np.clip(self.state, 0, 0.5)
	def replayHistory(self, history):
		steps = min(len(history['aGives']), len(history['bGives']))
		for t in range(steps):
			historySlice = {
				'aGives': history['aGives'][:t+1],
				'aKeeps': history['aKeeps'][:t+1],
				'bGives': history['bGives'][:t+1],
				'bKeeps': history['bKeeps'][:t+1],
			}
			self.update(historySlice)
	def reset(self):
		self.state = 1 if self.player=="A" else 0.5




class RLAgent(AgentBase):
	def act(self, money, history):
		state = self.getState(history, -1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.epsilon:
			a = np.random.randint(0, money+1)
		else:
			a = self.rlAct(state)
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep

	def getState(self, history, t):
		if len(history['aGives'])==0 or len(history['bGives'])==0 or t==0:
			return 0  # no history state
		if self.player == "A":
			myGives = history['aGives'][t]
			myKeeps = history['aKeeps'][t]
			otherGives = history['bGives'][t]
			otherKeeps = history['bKeeps'][t]
		else:
			myGives = history['bGives'][t]
			myKeeps = history['bKeeps'][t]
			otherGives = history['aGives'][t]
			otherKeeps = history['aKeeps'][t]
		if (otherGives==0 and otherKeeps==0) or (myGives==0 and myKeeps==0):
			return 1  # no information state
		myRatio = myGives / (myGives + myKeeps)
		otherRatio = otherGives / (otherGives + otherKeeps)
		# map this ratio into a discrete state space of size Q
		maxState = 0 if self.states <= 1 else self.states-1
		myState = int(myRatio * maxState)
		otherState = int(otherRatio * maxState)
		if self.rep == "other":
			state = myState
			assert 0 <= state <= self.states, "state outside limit"
		elif self.rep == "self-other":
			state = myState + self.states*otherState
			assert 0 <= state <= self.states**2, "state outside limit"
		return 2+state
	def reduceExploration(self, i, eMin=0, aMin=0):
		self.epsilon = max(eMin, np.exp(-i*self.decay))
		# self.alpha = max(aMin, np.exp(-i*self.decay))

class Bandit(RLAgent):
	def __init__(self, player, actions, rep="other", decay=0.1, alpha=1e0, ID="Bandit"):
		self.player = player
		self.ID = ID
		self.epsilon = 1.0
		self.states = 0
		self.alpha = alpha
		self.rep = rep  # filler
		self.decay = decay
		self.Q = np.zeros((actions))
		self.nA = np.zeros((actions))
	def rlAct(self, state):
		return np.argmax(self.Q)
	def learn(self, history):
		if self.player == "A":
			myGives = history['aGives']
			myRewards = history['aRewards']
		else:
			myGives = history['bGives']
			myRewards = history['bRewards']
		for t in range(len(history['aGives'])):
			a = myGives[t]
			r = myRewards[t]
			self.nA[a] += 1
			alpha = self.alpha / (self.nA[a])
			# alpha = self.alpha  # causes Q to explode
			self.Q[a] = alpha * (r + self.nA[a]*self.Q[a])
	def restart(self):
		self.epsilon = 1.0
		self.Q = np.zeros_like((self.Q))
		self.nA = np.zeros_like((self.nA))
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nA=self.nA)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.nA = data['nA']
	def restart(self):
		self.epsilon = 1.0
		self.alpha = 1.0
		self.Q = np.zeros_like((self.Q))
		self.nA = np.zeros_like((self.nA))


class QLearn(RLAgent):
	def __init__(self, player, actions, states, rep="other", gamma=0.9, decay=0.1, alpha=1e0, ID="QLearn"):
		self.player = player
		self.ID = ID
		self.states = states
		self.gamma = gamma
		self.epsilon = 1.0
		self.alpha = alpha
		self.decay = decay
		self.rep = rep
		if self.rep == "other":
			self.Q = np.zeros((2+states, actions))  # +2 for null states (see getState())
			self.nSA = np.zeros((2+states, actions))
		elif self.rep == "self-other":
			self.Q = np.zeros((2+states**2, actions))  # +2 for null states (see getState())
			self.nSA = np.zeros((2+states**2, actions))
	def rlAct(self, state):
		return np.argmax(self.Q[state, :])
	def learn(self, history):
		for t in np.arange(1, len(history['aGives'])):
			s = self.getState(history, t-1)
			snew = self.getState(history, t)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.nSA[s,a] += 1
			alpha = self.alpha / self.nSA[s,a]
			# alpha = self.alpha
			self.Q[s, a] += alpha * (r + self.gamma*np.max(self.Q[snew, :]) - self.Q[s, a])
	def restart(self):
		self.epsilon = 1.0
		# self.alpha = 1.0
		self.Q = np.zeros_like((self.Q))
		self.nSA = np.zeros_like((self.nSA))
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nSA=self.nSA)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.nSA = data['nSA']


# from Table 5,6 of Bowling and Veloso 2002
class Wolf(RLAgent):
	def __init__(self, player, actions, states, rep="other", gamma=0.9, decay=0.1, alpha=1e0, dW=2e-1, dL=4e-1, ID="Wolf"):
		self.player = player
		self.ID = ID
		self.epsilon = 1.0
		self.alpha = alpha
		self.states = states
		self.actions = actions
		self.gamma = gamma
		self.decay = decay
		self.dW = dW
		self.dL = dL
		self.rep = rep
		if self.rep == "other":
			self.Q = np.zeros((2+states, actions))  # +2 for null states (see getState())
			self.nSA = np.zeros((2+states, actions))
			self.pi = np.ones((2+states, actions)) / actions
			self.piBar = np.ones((2+states, actions)) / actions
		elif self.rep == "self-other":
			self.Q = np.zeros((2+states**2, actions))
			self.nSA = np.zeros((2+states**2, actions))
			self.pi = np.ones((2+states**2, actions)) / actions
			self.piBar = np.ones((2+states**2, actions)) / actions
	def rlAct(self, state):
		return np.argmax(self.pi[state, :])
		# return np.argmax(self.Q[state, :])
	def learn(self, history):
		for t in np.arange(1, len(history['aGives'])):
			s = self.getState(history, t-1)
			snew = self.getState(history, t)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			# standard Q-learning update of value function
			self.nSA[s,a] += 1
			alpha = self.alpha / self.nSA[s,a]
			# alpha = self.alpha
			self.Q[s,a] += alpha * (r + self.gamma*np.max(self.Q[snew, :]) - self.Q[s, a])
			Cs = np.sum(self.nSA[s,:])
			# variable learning rate
			aMax = np.argmax(self.Q[s,:])
			winning = np.sum(self.pi[s,:]*self.Q[s,:]) > np.sum(self.piBar[s,:]*self.Q[s,:])
			delta = self.dW if winning else self.dL
			for ap in range(self.actions):
				# update estimate of average policy				
				self.piBar[s,ap] += 1/Cs * (self.pi[s,ap] - self.piBar[s,ap])
			# step policy closer to optimal policy w.r.t Q
			dSA = 0
			if a != aMax:
				# dSA = -1
				dSA = -np.min([self.pi[s,a], delta/(self.actions-1)])
			else:
				# dSA = 1
				for ap in range(self.actions):
					if ap != a:
						dSA += np.min([self.pi[s, ap], delta/(self.actions-1)])
			# self.pi[s,a] = np.clip(self.pi[s,a] + dSA, 0, np.inf)
			self.pi[s,a] += dSA
	def restart(self):
		self.epsilon = 1.0
		# self.alpha = 1.0
		self.Q = np.zeros_like((self.Q))
		self.nSA = np.zeros_like((self.nSA))
		self.pi = np.ones_like((self.pi)) / self.actions
		self.piBar = np.ones_like((self.piBar)) / self.actions
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nSA=self.nSA, pi=self.pi, piBar=self.piBar)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.nSA = data['nSA']
		self.pi = data['pi']
		self.piBar = data['piBar']

class Hill(RLAgent):
	def __init__(self, player, actions, states, rep="other", decay=0.1, xi=1, nu=1e-4, gamma=0.9, alpha=1e0, ID="Hill"):
		self.player = player
		self.ID = ID
		self.epsilon = 1.0
		self.alpha = alpha
		self.xi = xi
		self.nu = nu
		self.gamma = gamma
		self.decay = decay
		self.states = states
		self.actions = actions
		self.rep = rep
		if self.rep == "other":
			self.Q = np.zeros((2+states, actions))
			self.pi = np.ones((2+states, actions)) / actions
			self.nSA = np.zeros((2+states, actions))
			self.delta = np.zeros((2+states, actions))
			self.V = np.zeros((2+states))
		elif self.rep == "self-other":
			self.Q = np.zeros((2+states**2, actions))
			self.pi = np.ones((2+states**2, actions)) / actions
			self.nSA = np.zeros((2+states**2, actions))
			self.delta = np.zeros((2+states**2, actions))
			self.V = np.zeros((2+states**2))
	def rlAct(self, state):
		return np.argmax(self.pi[state, :])
	def learn(self, history):
		for t in np.arange(1, len(history['aGives'])):
			s = self.getState(history, t-1)
			snew = self.getState(history, t)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.nSA[s,a] += 1
			alpha = self.alpha / self.nSA[s,a]				
			# alpha = self.alpha
			self.Q[s,a] += alpha * (r + self.gamma*np.max(self.Q[snew, :]) - self.Q[s, a])
			# Hill climbing policy update
			self.V[s] = np.sum(self.pi[s,:]*self.Q[s,:])
			for a in range(self.actions):
				if (1-self.pi[s,a]) == 0:
					self.delta[s,a] = (self.Q[s,a] - self.V[s])
				else:
					self.delta[s,a] = (self.Q[s,a] - self.V[s]) / (1-self.pi[s,a])
				# print(self.delta[s,a])
				delta = self.delta[s,a] - self.xi * np.abs(self.delta[s,a]) * self.pi[s,a]
				self.pi[s,a] += self.nu * delta
			self.pi[s] = softmax(self.pi[s])
	def restart(self):
		self.epsilon = 1.0
		# self.alpha = 1.0
		self.Q = np.zeros_like((self.Q))
		self.pi = np.zeros_like((self.pi))
		self.nSA = np.zeros_like(self.nSA)
		self.delta = np.zeros_like((self.delta))
		self.V = np.zeros_like((self.V))
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, pi=self.pi, nSA=self.nSA, delta=self.delta, V=self.V)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.pi = data['pi']
		self.nSA = data['nSA']
		self.delta = data['delta']
		self.V = data['V']


class ModelBased(RLAgent):
	def __init__(self, player, actions, states, rep="other", gamma=0.9, decay=0.1, ID="ModelBased"):
		self.player = player
		self.ID = ID
		self.epsilon = 1.0
		# self.alpha = 0
		self.states = states
		self.actions = actions
		self.gamma = gamma
		self.decay = decay
		self.rep = rep
		if self.rep == "other":
			self.R = np.zeros((2+states, actions))
			self.T = np.zeros((2+states, actions, 2+states))
			self.V = np.zeros((2+states))
			self.nSA = np.zeros((2+states, actions))
			self.nSAS = np.zeros((2+states, actions, 2+states))
			self.pi = np.zeros((2+states))
		elif self.rep == "self-other":
			self.R = np.zeros((2+states**2, actions))
			self.T = np.zeros((2+states**2, actions, 2+states**2))
			self.V = np.zeros((2+states**2))
			self.nSA = np.zeros((2+states**2, actions))
			self.nSAS = np.zeros((2+states**2, actions, 2+states**2))
			self.pi = np.zeros((2+states**2))
	def rlAct(self, state):
		return self.pi[state]
	def learn(self, history):
		for t in np.arange(1, len(history['aGives'])):
			s = self.getState(history, t-1)
			snew = self.getState(history, t)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.nSA[s,a] += 1
			self.nSAS[s,a,s] += 1
			self.T[s,a,:] = self.nSAS[s,a,:] / self.nSA[s,a]
			self.R[s,a] = (r + (self.nSA[s,a]-1) * self.R[s,a]) / self.nSA[s,a]
			nState = self.pi.shape[0]
			Tpi = np.zeros((nState, nState))
			Rpi = np.zeros((nState))
			for si in range(self.pi.shape[0]):
				a = int(self.pi[si])
				Tpi[si] = self.T[si,a]
				Rpi[si] = self.R[si,a]
			A = np.eye(nState) - self.gamma*Tpi
			B = Rpi
			self.V = np.linalg.solve(A, B)
			self.pi = np.argmax(self.R + self.gamma * (self.T @ self.V), axis=1)
	def restart(self):
		self.epsilon = 1.0
		self.R = np.zeros_like((self.R))
		self.T = np.zeros_like((self.T))
		self.V = np.zeros_like((self.V))
		self.nSA = np.zeros_like((self.nSA))
		self.nSAS = np.zeros_like((self.nSAS))
		self.pi = np.zeros_like((self.pi))
	def saveArchive(self, file):
		np.savez(file, R=self.R, T=self.T, V=self.V, nSA=self.nSA, nSAS=self.nSAS, pi=self.pi)
	def loadArchive(self, file):
		data = np.load(file)
		self.R = data['R']
		self.T = data['T']
		self.V = data['V']
		self.nSA = data['nSA']
		self.nSAS = data['nSAS']
		self.pi = data['pi']