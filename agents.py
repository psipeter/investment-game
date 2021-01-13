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
		return give, keep

class QAgent(AgentBase):
	def act(self, money, history):
		state = self.getState(history, t=-1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.epsilon:
			a = np.random.randint(0, money+1)
		# elif self.temp > 0:
		# 	probs = softmax(self.Q[state, :] / self.temp)
		# 	a = np.where(np.cumsum(probs) >= np.random.rand())[0][0]
		else:
			if hasattr(self, 'pi'):
				a = np.argmax(self.pi[state, :])
			else:
				a = np.argmax(self.Q[state, :])
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
		if otherGives==0 and otherKeeps==0:
			return 1  # no information state
		# ratio = otherGives / otherKeeps
		ratio = otherGives / (otherGives + otherKeeps)
		# map this ratio into a discrete state space of size Q
		state = int(ratio * self.states)
		assert 0 <= state <= self.states, "state outside limit"
		return 2+state
	def reduceExploration(self, i, epsilon0=10.0):
		self.epsilon = epsilon0 / (i+1)
	def reset(self):
		pass





class Generous(HardcodedAgent):
	def __init__(self, player, mean=1.0, std=0.1, epsilon=0.1, ID="Generous"):
		self.player = player
		self.ID = ID
		self.mean = mean
		self.std = std
		self.epsilon = epsilon
		self.state = 0
	def update(self, history):
		self.state = np.random.normal(self.mean, self.std)

class Greedy(HardcodedAgent):
	def __init__(self, player, mean=0.0, std=0.1, epsilon=0.1, ID="Greedy"):
		self.player = player
		self.ID = ID
		self.mean = mean
		self.std = std
		self.epsilon = epsilon
		self.state = 1
	def update(self, history):
		self.state = np.random.normal(self.mean, self.std)

class Accumulator(HardcodedAgent):
	def __init__(self, player, capital, alpha=2e-1, epsilon=0.1, ID="Accumulator"):
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
	def __init__(self, player, capital, epsilon=0.1, ID="TitForTat"):
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

class Bandit(AgentBase):
	def __init__(self, player, actions, epsilon=0.1, temp=0, ID="Bandit"):
		self.player = player
		self.ID = ID
		self.epsilon = epsilon
		self.Q = np.zeros((actions))
		self.nA = np.zeros((actions))
	def act(self, money, history):
		if money == 0:
			a = 0
		elif np.random.rand() < self.epsilon:
			a = np.random.randint(0, money+1)
		# elif self.temp > 0:
		# 	probs = softmax(self.Q / self.temp)
		# 	a = np.where(np.cumsum(probs) >= np.random.rand())[0][0]
		else:
			a = np.argmax(self.Q)
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
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
			self.Q[a] = (r + self.nA[a]*self.Q[a]) / (self.nA[a]+1)
	def reduceExploration(self, i, epsilon0=10.0):
		self.epsilon = epsilon0 / (i+1)
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nA=self.nA)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.nA = data['nA']

class QLearn(QAgent):
	def __init__(self, player, actions, states, alpha=1e-2, gamma=0.9, epsilon=0.1, temp=0, ID="QLearn"):
		self.player = player
		self.ID = ID
		self.epsilon = epsilon
		self.states = states
		self.alpha = alpha
		self.gamma = gamma
		self.Q = np.zeros((states+3, actions))  # +2 for null states (see getState())
		self.nSA = np.zeros((states+3, actions))
	def learn(self, history):
		for t in range(len(history['aGives'])-1):
			s = self.getState(history, t)
			snew = self.getState(history, t+1)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.nSA[s,a] += 1
			alpha = self.alpha / self.nSA[s,a]
			self.Q[s, a] += alpha * (r + self.gamma*np.max(self.Q[snew, :]) - self.Q[s, a])

class Wolf(QAgent):
	def __init__(self, player, actions, states, epsilon=0.1, ID="Wolf"):
		self.player = player
		self.ID = ID
		self.epsilon = epsilon
		self.states = states
		self.actions = actions
		self.Q = np.zeros((states+3, actions))
		self.nSA = np.zeros((states+3, actions))
		self.pi = np.ones((states+3, actions)) / actions
		self.piBar = np.ones((states+3, actions)) / actions
	def learn(self, history, alpha0=1e-2, dW=1e-1, dL=2e-1, gamma=0.99):
		for t in range(len(history['aGives'])-1):
			s = self.getState(history, t)
			snew = self.getState(history, t+1)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.nSA[s,a] += 1
			alpha = alpha0 / self.nSA[s,a]
			self.Q[s,a] += alpha * (r + gamma*np.max(self.Q[snew, :]) - self.Q[s, a])
			# Win or learn fast policy update
			Cs = np.sum(self.nSA[s,:])
			aGreedy = np.argmax(self.Q[s,:])
			condition = np.sum(self.pi[s,:]*self.Q[s,:]) > np.sum(self.piBar[s,:]*self.Q[s,:])
			delta = dW if condition else dL
			for a in range(self.actions):
				self.piBar[s,a] += 1/Cs * (self.pi[s,a] - self.piBar[s,a])
				if a != aGreedy:
					dSA = np.min([self.pi[s,a], delta/(self.actions-1)])
					update = -dSA
				else:
					update = 0
					for ap in range(self.actions):
						if ap == aGreedy:
							continue
						dSA = np.min([self.pi[s, ap], delta/(self.actions-1)])
						update += dSA
				self.pi[s, a] += update

class Hill(QAgent):
	def __init__(self, player, actions, states,
			epsilon=0.1, alpha=3e-2, xi=0.95, nu=1e-2, gamma=0.9, ID="Hill"):
		self.player = player
		self.ID = ID
		self.epsilon = epsilon
		self.alpha = alpha
		self.xi = xi
		self.nu = nu
		self.gamma = gamma
		self.states = states
		self.actions = actions
		self.Q = np.zeros((states+3, actions))
		self.pi = np.ones((states+3, actions)) / actions
		self.delta = np.zeros((states+3, actions))
		self.V = np.zeros((states+3))
	def learn(self, history):
		for t in range(len(history['aGives'])-1):
			s = self.getState(history, t)
			snew = self.getState(history, t+1)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.Q[s,a] += self.alpha * (r + self.gamma*np.max(self.Q[snew, :]) - self.Q[s, a])
			# Hill climbing policy update
			self.V[s] = np.sum(self.pi[s,:]*self.Q[s,:])
			for a in range(self.actions):
				if (1-self.pi[s,a]) == 0:
					self.delta[s,a] = (self.Q[s,a] - self.V[s])
				else:
					self.delta[s,a] = (self.Q[s,a] - self.V[s]) / (1-self.pi[s,a])
				delta = self.delta[s,a] - self.xi * np.abs(self.delta[s,a]) * self.pi[s,a]
				self.pi[s,a] += self.nu * delta


class ModelBased(QAgent):
	def __init__(self, player, actions, states, epsilon=0.1, gamma=0.9, ID="ModelBased"):
		self.player = player
		self.ID = ID
		self.epsilon = epsilon
		self.states = states
		self.actions = actions
		self.epsilon = epsilon
		self.gamma = gamma
		self.R = np.zeros((states+3, actions))
		self.T = np.zeros((states+3, actions, states+3))
		self.V = np.zeros((states+3))
		self.nSA = np.zeros((states+3, actions))
		self.nSAS = np.zeros((states+3, actions, states+3))
		self.pi = np.zeros((states+3))
	def act(self, money, history):
		state = self.getState(history, t=-1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.epsilon:
			a = np.random.randint(0, money+1)
		else:
			a = self.pi[state]
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def learn(self, history):
		for t in range(len(history['aGives'])-1):
			s = self.getState(history, t)
			snew = self.getState(history, t+1)
			a = history['aGives'][t] if self.player == "A" else history['bGives'][t]
			r = history['aRewards'][t] if self.player == "A" else history['bRewards'][t]
			self.nSA[s,a] += 1
			self.nSAS[s,a,s] += 1
			self.T[s,a,:] = self.nSAS[s,a,:] / self.nSA[s,a]
			self.R[s,a] = (r + (self.nSA[s,a]-1) * self.R[s,a]) / self.nSA[s,a]
			Tpi = np.zeros((self.states+3, self.states+3))
			Rpi = np.zeros((self.states+3))
			for si in range(self.states+3):
				a = int(self.pi[si])
				Tpi[si] = self.T[si,a]
				Rpi[si] = self.R[si,a]
			A = np.eye(self.states+3) - self.gamma*Tpi
			B = Rpi
			self.V = np.linalg.solve(A, B)
			self.pi = np.argmax(self.R + self.gamma * (self.T @ self.V), axis=1)
	def reduceExploration(self, i, decay=0.95):
		self.epsilon = decay**i
