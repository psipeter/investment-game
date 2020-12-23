import numpy as np
from scipy.special import softmax
import random

class Agent():
	def __init__(self):
		self.ID = None
		self.myActions = []
		self.otherActions = []
		self.rewards = []
		self.nInvestor = 0
		self.nReturner = 0
		self.tournamentRewards = {}
		self.tournamentActive = True
		self.player = None
		self.learning = True
		self.state = 1
		self.iter = 0

	def update(self):
		pass

	def tournamentUpdate(self, player, r):
		if player == "A":
			self.nInvestor += 1
		if player == "B":
			self.nReturner += 1
		if r not in self.tournamentRewards:
			self.tournamentRewards[r] = []
		self.tournamentRewards[r].append(np.mean(self.rewards))
		self.reset()

	def reset(self):
		self.myActions = []
		self.otherActions = []
		self.rewards = []
		self.state = 1

	def fullReset(self):
		self.reset()
		self.iter = 0
		# self.learning = True

	def setPlayer(self, player):
		self.player = player

	def saveModel(self):
		pass

	def loadModel(self):
		pass


''' NON-LEARNERS '''


class Gaussian(Agent):
	def __init__(self, mean, std=0.1, epsilon=0.01, ID="Gaussian"):
		super().__init__()
		self.ID = ID
		self.mean = mean
		self.std = std
		self.epsilon = epsilon

	def action(self, money):
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		else:
			action = np.clip(int(money*np.random.normal(self.mean, self.std)), 0, money)
		return action



class Dynamic(Agent):
	def __init__(self, func, ID, epsilon=0.01):
		super().__init__()
		self.ID = ID
		self.func = func
		self.iter = 0
		self.state = self.func(self.iter)
		self.epsilon = epsilon

	def action(self, money):
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		else:
			action = np.clip(np.int(money*self.state), 0, money)
		return action

	def update(self):
		self.iter += 1
		self.state = self.func(self.iter)

	def reset(self):
		super().reset()
		self.iter = 0
		self.state = self.func(self.iter)




class Accumulator(Agent):
	def __init__(self, env, maxReturn=0.5, alpha=2e-1, epsilon=0.01, ID="Accumulator"):
		super().__init__()
		self.ID = ID
		self.capital = env.capital
		self.maxReturn = maxReturn
		self.alpha = alpha
		self.epsilon = epsilon

	def action(self, money):
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		else:
			action = np.clip(int(money*self.state), 0, money)
		return action

	def update(self):
		if self.player == "A":
			if self.otherActions[-1] > self.myActions[-1]:
				judgement = 1
			elif self.otherActions[-1] == self.myActions[-1]:
				judgement = 0
			else:
				judgement = -1
			self.state += self.alpha * judgement
			self.state = np.clip(self.state, 0, 1)
		elif self.player == "B":
			if self.otherActions[-1] == self.capital:
				judgement = 1
			else:
				judgement = -1
			self.state += self.alpha * judgement
			self.state = np.clip(self.state, 0, self.maxReturn)

	def setPlayer(self, player):
		self.player = player
		self.state = 1 if self.player == "A" else 0.5


class TitForTat(Agent):
	def __init__(self, env, epsilon=0.01, strategy="Fair"):
		super().__init__()
		self.ID = "Tit-for-Tat" # +strategy
		self.capital = env.capital
		self.matchFactor = env.matchFactor
		self.strategy = strategy
		self.epsilon = epsilon

	def action(self, money):
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		else:
			action = np.clip(int(money*self.state), 0, money)
		return action

	def update(self):
		if self.player == "A":
			if self.myActions[-1] == 0:
				self.state = 0  # stay greedy (still epsilon-random actions)
				# self.state = np.random.rand()  # random action
			else:
				if self.strategy == "Fair":
					# happy if returner gave 50% of matched investment
					self.state =  self.otherActions[-1] / (0.5*self.myActions[-1]*self.matchFactor)
				elif self.strategy == "Gain":
					# happy if return was greater than investment
					self.state = self.otherActions[-1] / self.myActions[-1]
			self.state = np.clip(self.state, 0, 1)
		elif self.player == "B":
			self.state = self.otherActions[-1] / self.capital  # happy if investor gave 100% of capital
			self.state = np.clip(self.state/2, 0, 0.5)

	def setPlayer(self, player):
		self.player = player
		self.state = 1 if self.player == "A" else 0.5


''' LEARNERS '''



class FMQ(Agent):
	def __init__(self, env, alpha=3e-2, temp=10, decay=0.95, epsilon=0.01, learnVsHumans=False, ID="FMQ"):
		super().__init__()
		self.ID = ID
		self.epsilon = epsilon
		self.capital = env.capital 
		self.matchFactor = env.matchFactor
		self.nActions = self.matchFactor*self.capital+1
		self.QA = np.zeros((self.nActions))
		self.rMaxA = np.zeros((self.nActions))
		self.cMaxA = np.zeros((self.nActions))
		self.cA = np.zeros((self.nActions))
		self.QB = np.zeros((self.nActions))
		self.rMaxB = np.zeros((self.nActions))
		self.cMaxB = np.zeros((self.nActions))
		self.cB = np.zeros((self.nActions))
		self.decay = decay
		self.temp = temp
		self.alpha = alpha
		self.learnVsHumans = learnVsHumans

	def action(self, money):
		temp = self.temp * self.decay**self.iter
		Q = self.QA if self.player == "A" else self.QB
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		elif temp > 0:
			probs = softmax(Q / temp)
			action = np.where(np.cumsum(probs) >= np.random.rand())[0][0]
		else:
			action = np.argmax(Q)
		return np.clip(action, 0, money)

	def update(self):
		if len(self.otherActions) > 1 and self.learning:
			Q = self.QA if self.player == "A" else self.QB
			rMax = self.rMaxA if self.player == "A" else self.rMaxB
			cMax = self.cMaxA if self.player == "A" else self.cMaxB
			c = self.cA if self.player == "A" else self.cB
			action = self.myActions[-1]
			reward = self.rewards[-1]
			if reward > rMax[action]:
				rMax[action] = reward
				cMax[action] = 1
			elif reward == rMax[action]:
				cMax[action] += 1
			c[action] += 1
			alpha = self.alpha / c[action]
			Q[action] += alpha * rMax[action]*cMax[action]/c[action]

	def reset(self):
		super().reset()
		self.iter += 1

	def fullReset(self):
		super().fullReset()
		self.QA = np.zeros((self.nActions))
		self.rMaxA = np.zeros((self.nActions))
		self.cMaxA = np.zeros((self.nActions))
		self.cA = np.zeros((self.nActions))
		self.QB = np.zeros((self.nActions))
		self.rMaxB = np.zeros((self.nActions))
		self.cMaxB = np.zeros((self.nActions))
		self.cB = np.zeros((self.nActions))

	def saveModel(self):
		prefix = "game/" if self.learnVsHumans else ""
		suffix = "_Human" if self.learnVsHumans else ""
		np.savez("%sdata/FMQ%s.npz"%(prefix, suffix),
			QA=self.QA,
			rMaxA=self.rMaxA,
			cMaxA=self.cMaxA,
			cA=self.cA,
			QB=self.QB,
			rMaxB=self.rMaxB,
			cMaxB=self.cMaxB,
			cB=self.cB)

	def loadModel(self):
		suffix = "_Human" if self.learnVsHumans else ""
		data = np.load("game/data/FMQ%s.npz"%suffix)
		self.QA = data['QA']
		self.rMaxA = data['rMaxA']
		self.cMaxA = data['cMaxA']
		self.cA = data['cA']
		self.QB = data['QB']
		self.rMaxB = data['rMaxB']
		self.cMaxB = data['cMaxB']
		self.cB = data['cB']
		self.learning = True if self.learnVsHumans else False


class WoLFPHC(Agent):
	def __init__(self, env, alpha=3e-2, deltaW=2e-1, deltaL=1e-1, firstMove="Generous",
			temp=10, decay=0.95, gamma=0.99, epsilon=0.01, learnVsHumans=False, ID="WoLF-PHC"):
		super().__init__()
		self.ID = ID
		self.epsilon = epsilon
		self.capital = env.capital 
		self.matchFactor = env.matchFactor
		self.nActions = self.matchFactor*self.capital+1
		self.nStates = 2*self.matchFactor*(self.capital+1)*(self.capital+1)
		self.Q = np.zeros((self.nActions, self.nStates))
		self.nAS = np.zeros((self.nActions, self.nStates))
		self.pi = np.ones((self.nActions, self.nStates)) / self.nActions
		self.piBar = np.ones((self.nActions, self.nStates)) / self.nActions
		self.decay = decay
		self.gamma = gamma
		self.temp = temp
		self.deltaW = deltaW
		self.deltaL = deltaL
		self.alpha = alpha
		self.firstMove = firstMove
		self.learnVsHumans = learnVsHumans

	def action(self, money):
		temp = self.temp * self.decay**self.iter
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		elif len(self.otherActions) < 1:
			if self.firstMove == "Generous":
				action = money if self.player == "A" else int(money/2)
			elif self.firstMove == "Random":
				action = np.random.randint(0, money) if money > 0 else 0
		elif temp > 0:
			state = self.getState(-1)
			probs = softmax(self.pi[:, state] / temp, axis=0)
			action = np.where(np.cumsum(probs) >= np.random.rand())[0][0]
		else:
			state = self.getState(-1)
			action = np.argmax(self.pi[:, state])
		return np.clip(action, 0, money)

	def getState(self, idx=-1):
		k = self.matchFactor * self.capital+1 if self.player == "A" else 1
		l = 1 if self.player == "A" else self.matchFactor * self.capital+1
		m = 0 if self.player == "A" else int(self.nStates/2)
		return m + k*self.myActions[idx] + l*self.otherActions[idx]

	def update(self):
		if len(self.otherActions) > 1:
			# normal Q-update
			state = self.getState(-2)
			stateNew = self.getState(-1)
			action = self.myActions[-1]
			if self.learning:
				reward = self.rewards[-1]
				self.nAS[action, state] += 1
				alpha = self.alpha / self.nAS[action, state]
				self.Q[action, state] += alpha * (reward + self.gamma*np.max(self.Q[:, stateNew]) - self.Q[action, state])
				# WoLF policy update
				Cs = np.sum(self.nAS[:, state])
				temp = self.temp * self.decay**self.iter
				aGreedy = np.argmax(self.Q[:, state])
				condition = np.sum(self.pi[:, state]*self.Q[:, state]) > np.sum(self.piBar[:, state]*self.Q[:, state])
				delta = self.deltaW if condition else self.deltaL
				for a in range(self.nActions):
					self.piBar[a, state] += 1/Cs * (self.pi[a, state] - self.piBar[a, state])
					if a != aGreedy:
						deltaSA = np.min([self.pi[a, state], delta/(self.nActions-1)])
						DeltaSA = -deltaSA
					else:
						DeltaSA = 0
						for ap in range(self.nActions):
							if ap == aGreedy: continue
							deltaSA = np.min([self.pi[ap, state], delta/(self.nActions-1)])
							DeltaSA += deltaSA
					self.pi[a, state] += DeltaSA

	def reset(self):
		super().reset()
		self.iter += 1

	def fullReset(self):
		super().fullReset()
		self.Q = np.zeros((self.nActions, self.nStates))
		self.nAS = np.zeros((self.nActions, self.nStates))
		self.pi = np.ones((self.nActions, self.nStates)) / self.nActions
		self.piBar = np.ones((self.nActions, self.nStates)) / self.nActions

	def saveModel(self):
		prefix = "game/" if self.learnVsHumans else ""
		suffix = "_Human" if self.learnVsHumans else ""
		np.savez("%sdata/WoLFPHC%s.npz"%(prefix, suffix),
			Q=self.Q,
			nAS=self.nAS,
			pi=self.pi,
			piBar=self.piBar)

	def loadModel(self):
		suffix = "_Human" if self.learnVsHumans else ""
		data = np.load("game/data/WoLFPHC%s.npz"%suffix)
		self.Q = data['Q']
		self.nAS = data['nAS']
		self.pi = data['pi']
		self.piBar = data['piBar']
		self.learning = True if self.learnVsHumans else False


class PGAAPP(Agent):
	def __init__(self, env, alpha=3e-2, nu=1e-2, gamma=0.95, xi=0.95, firstMove="Generous",
			temp=10, decay=0.9, epsilon=0.01, learnVsHumans=False, ID="PGA-APP"):
		super().__init__()
		self.ID = ID
		self.epsilon = epsilon
		self.capital = env.capital 
		self.matchFactor = env.matchFactor
		self.nActions = self.matchFactor*self.capital+1
		self.nStates = 2*self.matchFactor*(self.capital+1)*(self.capital+1)
		self.Q = np.zeros((self.nActions, self.nStates))
		self.pi = np.ones((self.nActions, self.nStates)) / self.nActions
		self.delta = np.zeros((self.nActions, self.nStates))
		self.V = np.zeros((self.nStates))
		self.decay = decay
		self.alpha = alpha  # theta in original paper
		self.nu = nu
		self.xi = xi  # gamma in original paper
		self.gamma = gamma  # xi in original paper
		self.temp = temp
		self.firstMove = firstMove
		self.learnVsHumans = learnVsHumans

	def action(self, money):
		temp = self.temp * self.decay**self.iter
		if np.random.rand() < self.epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		elif len(self.otherActions) < 1:
			if self.firstMove == "Generous":
				action = money if self.player == "A" else int(money/2)
			elif self.firstMove == "Random":
				action = np.random.randint(0, money) if money > 0 else 0
		elif temp > 0:
			state = self.getState(-1)
			# probs = softmax(self.pi[:, state] / temp, axis=0)
			probs = self.pi[:, state]
			action = np.where(np.cumsum(probs) >= np.random.rand())[0][0]
		else:
			state = self.getState(-1)
			action = np.argmax(self.pi[:, state])
		return np.clip(action, 0, money)

	def getState(self, idx=-1):
		k = self.matchFactor * self.capital+1 if self.player == "A" else 1
		l = 1 if self.player == "A" else self.matchFactor * self.capital+1
		m = 0 if self.player == "A" else int(self.nStates/2)
		return m + k*self.myActions[idx] + l*self.otherActions[idx]

	def update(self):
		if len(self.otherActions) > 1:
			state = self.getState(-2)
			stateNew = self.getState(-1)
			action = self.myActions[-1]
			if self.learning:
				reward = self.rewards[-1]
				self.Q[action, state] += self.alpha*(reward - self.Q[action, state] + self.gamma*np.max(self.Q[:, stateNew]))
				self.V[state] = np.sum(self.pi[:, state]*self.Q[:, state])
				for a in range(self.nActions):
					if (1-self.pi[a, state]) == 0:
						self.delta[a, state] = (self.Q[a, state] - self.V[state])
					else:
						self.delta[a, state] = (self.Q[a, state] - self.V[state]) / (1-self.pi[a, state])
					delta = self.delta[a, state] - self.xi * np.abs(self.delta[a, state]) * self.pi[a, state]
					self.pi[a, state] += self.nu * delta
				# why is this necessary?
				temp = self.temp * self.decay**self.iter	
				if temp > 0:		
					self.pi[:, state] = softmax(self.pi[:, state] / temp, axis=0)

	def reset(self):
		super().reset()
		self.iter += 1

	def fullReset(self):
		super().fullReset()
		self.Q = np.zeros((self.nActions, self.nStates))
		self.pi = np.ones((self.nActions, self.nStates)) / self.nActions
		self.delta = np.zeros((self.nActions, self.nStates))
		self.V = np.zeros((self.nStates))

	def saveModel(self):
		prefix = "game/" if self.learnVsHumans else ""
		suffix = "_Human" if self.learnVsHumans else ""
		np.savez("%sdata/PGAAPP%s.npz"%(prefix, suffix),
			Q=self.Q,
			pi=self.pi,
			delta=self.delta,
			V=self.V)

	def loadModel(self):
		suffix = "_Human" if self.learnVsHumans else ""
		data = np.load("game/data/PGAAPP%s.npz"%suffix)
		self.Q = data['Q']
		self.pi = data['pi']
		self.delta = data['delta']
		self.V = data['V']
		self.learning = True if self.learnVsHumans else False


class ModelBased(Agent):
	def __init__(self, env, updateFreq=10, decay=0.95, gamma=0.99, epsilon=0.01,
			learnVsHumans=False, firstMove="Generous", ID="Model-Based"):
		super().__init__()
		self.ID = ID
		self.capital = env.capital 
		self.matchFactor = env.matchFactor
		self.nActions = self.matchFactor*self.capital+1
		self.nStates = 2*self.matchFactor*(self.capital+1)*(self.capital+1)
		self.R = np.zeros((self.nActions, self.nStates))
		self.T = np.zeros((self.nActions, self.nStates, self.nStates)) # / nStates
		self.V = np.zeros((self.nStates))
		self.nAS = np.zeros((self.nActions, self.nStates))
		self.nASS = np.zeros((self.nActions, self.nStates, self.nStates))
		self.pi = np.zeros((self.nStates), dtype=int)
		self.decay = decay
		self.gamma = gamma
		self.gameIter = 0
		self.epsilon = epsilon
		self.updateFreq = updateFreq
		self.firstMove = firstMove
		self.learnVsHumans = learnVsHumans

	def action(self, money):
		epsilon = self.epsilon + self.decay**self.iter
		if np.random.rand() < epsilon:
			action = np.random.randint(0, money) if money > 0 else 0
		elif len(self.otherActions) < 1:
			if self.firstMove == "Generous":
				action = money if self.player == "A" else int(money/2)
			elif self.firstMove == "Random":
				action = np.random.randint(0, money) if money > 0 else 0
		else:
			state = self.getState(-1)
			action = self.pi[state]
		self.gameIter += 1
		return np.clip(action, 0, money)

	def getState(self, idx=-1):
		k = self.matchFactor * self.capital+1 if self.player == "A" else 1
		l = 1 if self.player == "A" else self.matchFactor * self.capital+1
		m = 0 if self.player == "A" else int(self.nStates/2)
		return m + k*self.myActions[idx] + l*self.otherActions[idx]

	def update(self):
		if len(self.otherActions) > 1:
			state = self.getState(-2)
			stateNew = self.getState(-1)
			action = self.myActions[-1]
			if self.learning:
				reward = self.rewards[-1]
				self.nAS[action, state] += 1
				self.nASS[action, state, stateNew] += 1
				self.T[action, state, :] = self.nASS[action, state, :] / self.nAS[action, state]
				self.R[action, state] = (reward + (self.nAS[action, state]-1) * self.R[action, state]) / self.nAS[action, state]
				if self.gameIter % self.updateFreq == 0:
					Tpi = np.zeros((self.nStates, self.nStates))
					Rpi = np.zeros((self.nStates))
					for si in range(self.nStates):
						a = self.pi[si]
						Tpi[si] = self.T[a, si]
						Rpi[si] = self.R[a, si]
					A = np.eye(self.nStates) - self.gamma*Tpi
					B = Rpi
					self.V = np.linalg.solve(A, B)
				self.pi = np.argmax(self.R + self.gamma * (self.T @ self.V), axis=0)

	def reset(self):
		super().reset()
		self.iter += 1
		self.gameIter = 0

	def fullReset(self):
		super().fullReset()
		self.R = np.zeros((self.nActions, self.nStates))
		self.T = np.zeros((self.nActions, self.nStates, self.nStates)) # / nStates
		self.V = np.zeros((self.nStates))
		self.nAS = np.zeros((self.nActions, self.nStates))
		self.nASS = np.zeros((self.nActions, self.nStates, self.nStates))
		self.pi = np.zeros((self.nStates), dtype=int)

	def saveModel(self):
		prefix = "game/" if self.learnVsHumans else ""
		suffix = "_Human" if self.learnVsHumans else ""
		np.savez("%sdata/ModelBased%s.npz"%(prefix, suffix),
			R=self.R,
			T=self.T,
			V=self.V,
			nASS=self.nASS,
			pi=self.pi)

	def loadModel(self):
		suffix = "_Human" if self.learnVsHumans else ""
		data = np.load("game/data/ModelBased%s.npz"%suffix)
		self.R = data['R']
		self.T = data['T']
		self.V = data['V']
		self.nASS = data['nASS']
		self.pi = data['pi']
		self.learning = True if self.learnVsHumans else False