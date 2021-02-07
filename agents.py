import numpy as np
from scipy.special import softmax
import random

class AgentBase():
	def act(self, money, history):
		pass
	def setState(self, history, t):
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
	def saveArchive(self, file):
		pass	
	def loadArchive(self, file):
		pass

class HardcodedAgent(AgentBase):
	def act(self, money, history):
		self.update(history)
		if money == 0:
			a = 0
		elif np.random.rand() < self.E:
			a = np.random.randint(0, money+1)
		else:
			a = money * self.state
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def reset(self):
		self.state = 0

class Generous(HardcodedAgent):
	def __init__(self, player, mean=1.0, std=0.05, E=0, ID="Generous"):
		self.player = player
		self.ID = ID
		self.mean = mean
		self.std = std
		self.E = E
		self.state = 0
	def update(self, history):
		self.state = np.random.normal(self.mean, self.std)

class Greedy(HardcodedAgent):
	def __init__(self, player, mean=0.0, std=0.05, E=0, ID="Greedy"):
		self.player = player
		self.ID = ID
		self.mean = mean
		self.std = std
		self.E = E
		self.state = 1
	def update(self, history):
		self.state = np.random.normal(self.mean, self.std)

class T4T(HardcodedAgent):
	def __init__(self, player, F=0.5, P=1.0, E=0, ID="T4T"):
		self.player = player
		self.ID = ID
		self.F = F  # rate of forgiveness (state increase with opponent generosity)
		self.P = P  # rate of punishment (state decrease with opponent greed)
		assert F >= 0, "forgiveness rate must be positive or zero"
		assert P >= 0, "punishment rate must be positive or zero"
		self.E = E
		self.state = 1.0 if self.player=="A" else 0.5
		self.maxGive = 1.0 if self.player=="A" else 0.5
	def update(self, history):
		if len(history['aGives'])==0 or len(history['bGives'])==0:
			return
		if self.player == "A":
			otherGive = history['bGives'][-1]
			otherKeep = history['bKeeps'][-1]
			# delta proportional to give minus keep
			# unless no information (because A gave 0), in which case forgive a bit
			delta = (otherGive-otherKeep)/(otherGive+otherKeep) if otherGive+otherKeep>0 else 0.1
		else:
			otherGive = history['aGives'][-1]
			otherKeep = history['aKeeps'][-1]
			# delta positive if A invested maximum
			# otherwise negative depending on the amount kept
			delta = 1 if otherKeep==0 else -otherKeep/(otherGive+otherKeep)
		self.state += delta*self.F if delta>0 else delta*self.P
		self.state = np.clip(self.state, 0, self.maxGive)
	def reset(self):
		self.state = 1.0 if self.player=="A" else 0.5
		self.maxGive = 1.0 if self.player=="A" else 0.5


class RLAgent(AgentBase):
	def setState(self, history, t):
		if len(history['aGives'])==0 or len(history['bGives'])==0:
			self.state = 0  # no history state
			return
		if self.player == "A":
			myGive = history['aGives'][t]
			myKeep = history['aKeeps'][t]
			otherGive = history['bGives'][t]
			otherKeep = history['bKeeps'][t]
		else:
			myGive = history['bGives'][t]
			myKeep = history['bKeeps'][t]
			otherGive = history['aGives'][t]
			otherKeep = history['aKeeps'][t]
		if (otherGive==0 and otherKeep==0) or (myGive==0 and myKeep==0):
			self.state = 1  # no information state
			return
		myRatio = myGive / (myGive + myKeep)
		otherRatio = otherGive / (otherGive + otherKeep)
		# map this ratio into a discrete state space of size Q
		maxState = 0 if self.nS <= 1 else self.nS-1
		myState = int(myRatio * maxState)
		otherState = int(otherRatio * maxState)
		state = otherState
		assert 0 <= state <= self.nS, "state outside limit"
		self.state = 2+state
	def reset(self):
		self.state = 0

class Bandit(RLAgent):
	def __init__(self, player, nA, E=0, T=100, rS=1, rO=0, dE=0.9, dT=0.9, ID="Bandit"):
		self.player = player
		self.nA = nA
		self.state = 0
		self.nS = 0
		self.ID = ID
		self.E = E  # epsilon random action
		self.T = T  # temperature for Boltzmann exploration
		self.E0 = E
		self.T0 = T
		self.rS = rS  # weight for selfish reward
		self.rO = rO  # weight for prosocial reward
		self.dE = dE  # epsilon decay
		self.dT = dT  # temperature decay
		self.Q = np.zeros((nA))  # value function
		self.cA = np.zeros((nA))  # visits to each action
	def act(self, money, history):
		self.setState(history, -1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.E:
			a = np.random.randint(0, money+1)
		elif self.T > 0:
			prob = softmax(self.Q / self.T)
			a = np.where(np.cumsum(prob) >= np.random.rand())[0][0]
		else:
			a = np.argmax(self.Q)
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def learn(self, history):
		if self.player == "A":
			myGives = history['aGives']
			myRewards = history['aRewards']
			myStates = history['aStates']
			otherRewards = history['bRewards']
		else:
			myGives = history['bGives']
			myRewards = history['bRewards']
			myStates = history['bStates']
			otherRewards = history['aRewards']
		for t in range(len(myGives)-1):
			s = myStates[t]
			snew = myStates[t+1]
			a = myGives[t]
			r = (self.rS*myRewards[t]+self.rO*otherRewards[t])/(self.rS+self.rO)
			self.cA[a] += 1
			self.Q[a] = (r + self.cA[a]*self.Q[a]) / (self.cA[a] + 1)
	def reduceExploration(self, i):
		self.E *= self.dE
		self.T *= self.dT
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nA=self.cA)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.cA = data['nA']
	def restart(self):
		self.E = self.E0
		self.T = self.T0
		self.Q = np.zeros_like((self.Q))
		self.cA = np.zeros_like((self.cA))



class QLearn(RLAgent):
	def __init__(self, player, nA, nS, E=0, T=100, L=1, G=0.9, rS=1, rO=0, dE=0.9, dL=0.9, dT=0.9, ID="QLearn"):
		self.player = player
		self.ID = ID
		self.nA = nA
		self.state = 0
		self.nS = nS
		self.G = G
		self.E = E
		self.L = L
		self.T = T
		self.E0 = E
		self.L0 = L
		self.T0 = T
		self.dE = dE
		self.dL = dL
		self.dT = dT
		self.rS = rS  # weight for selfish reward
		self.rO = rO  # weight for prosocial reward
		self.Q = np.zeros((2+nS, nA))
		self.cSA = np.zeros((2+nS, nA))
	def act(self, money, history):
		self.setState(history, -1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.E:
			a = np.random.randint(0, money+1)
		elif self.T > 0:
			prob = softmax(self.Q[self.state] / self.T)
			a = np.where(np.cumsum(prob) >= np.random.rand())[0][0]
		else:
			a = np.argmax(self.Q[self.state])
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def learn(self, history):
		if self.player == "A":
			myGives = history['aGives']
			myRewards = history['aRewards']
			myStates = history['aStates']
			otherRewards = history['bRewards']
		else:
			myGives = history['bGives']
			myRewards = history['bRewards']
			myStates = history['bStates']
			otherRewards = history['aRewards']
		for t in range(len(myGives)-1):
			s = myStates[t]
			snew = myStates[t+1]
			a = myGives[t]
			r = (self.rS*myRewards[t]+self.rO*otherRewards[t])/(self.rS+self.rO)
			self.cSA[s,a] += 1
			# L = self.L / self.cSA[s,a]
			L = self.L
			self.Q[s, a] += L * (r + self.G*np.max(self.Q[snew, :]) - self.Q[s, a])
	def restart(self):
		self.E = self.E0
		self.L = self.L0
		self.T = self.T0
		self.Q = np.zeros_like((self.Q))
		self.cSA = np.zeros_like((self.cSA))
	def reduceExploration(self, i):
		self.E *= self.dE
		self.L *= self.dL
		self.T *= self.dT
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nSA=self.cSA)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.cSA = data['nSA']


# from Table 5,6 of Bowling and Veloso 2002
class Wolf(RLAgent):
	def __init__(self, player, nA, nS, E=0, T=100, L=1, G=0.9, rS=1, rO=0, dE=0.9, dL=0.9, dT=0.9, dW=1e-1, dN=2e-1, ID="Wolf"):
		self.player = player
		self.ID = ID
		self.state = 0
		self.nS = nS
		self.nA = nA
		self.G = G
		self.E = E
		self.L = L
		self.T = T
		self.E0 = E
		self.L0 = L
		self.T0 = T
		self.dE = dE
		self.dL = dL
		self.dT = dT
		self.dW = dW
		self.dN = dN
		self.rS = rS  # weight for selfish reward
		self.rO = rO  # weight for prosocial reward
		self.Q = np.zeros((2+nS, nA))  # +2 for null nS (see setState())
		self.cSA = np.zeros((2+nS, nA))
		self.pi = np.ones((2+nS, nA)) / nA
		self.piBar = np.ones((2+nS, nA)) / nA
	def act(self, money, history):
		self.setState(history, -1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.E:
			a = np.random.randint(0, money+1)
		elif self.T > 0:
			prob = softmax(self.pi[self.state] / self.T)
			a = np.where(np.cumsum(prob) >= np.random.rand())[0][0]
		else:
			a = np.argmax(self.pi[self.state])
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def learn(self, history):
		if self.player == "A":
			myGives = history['aGives']
			myRewards = history['aRewards']
			myStates = history['aStates']
			otherRewards = history['bRewards']
		else:
			myGives = history['bGives']
			myRewards = history['bRewards']
			myStates = history['bStates']
			otherRewards = history['aRewards']
		for t in range(len(myGives)-1):
			s = myStates[t]
			snew = myStates[t+1]
			a = myGives[t]
			r = (self.rS*myRewards[t]+self.rO*otherRewards[t])/(self.rS+self.rO)
			# standard Q-learning update of value function
			self.cSA[s,a] += 1
			# L = self.L / self.cSA[s,a]
			L = self.L
			self.Q[s,a] += L * (r + self.G*np.max(self.Q[snew, :]) - self.Q[s, a])
			Cs = np.sum(self.cSA[s,:])
			# variable learning rate
			aMax = np.argmax(self.Q[s,:])
			winning = np.sum(self.pi[s,:]*self.Q[s,:]) > np.sum(self.piBar[s,:]*self.Q[s,:])
			delta = self.dW if winning else self.dN
			for ap in range(self.nA):
				# update estimate of average policy				
				self.piBar[s,ap] += 1/Cs * (self.pi[s,ap] - self.piBar[s,ap])
			# step policy closer to optimal policy w.r.t Q
			dSA = 0
			if a != aMax:
				# dSA = -1
				dSA = -np.min([self.pi[s,a], delta/(self.nA-1)])
			else:
				# dSA = 1
				for ap in range(self.nA):
					if ap != a:
						dSA += np.min([self.pi[s, ap], delta/(self.nA-1)])
			# self.pi[s,a] = np.clip(self.pi[s,a] + dSA, 0, np.inf)
			self.pi[s,a] += dSA
	def restart(self):
		self.E = self.E0
		self.L = self.L0
		self.T = self.T0
		self.Q = np.zeros_like((self.Q))
		self.cSA = np.zeros_like((self.cSA))
		self.pi = np.ones_like((self.pi)) / self.nA
		self.piBar = np.ones_like((self.piBar)) / self.nA
	def reduceExploration(self, i):
		self.E *= self.dE
		self.L *= self.dL
		self.T *= self.dT
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, nSA=self.cSA, pi=self.pi, piBar=self.piBar)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.cSA = data['nSA']
		self.pi = data['pi']
		self.piBar = data['piBar']

class Hill(RLAgent):
	def __init__(self, player, nA, nS, E=0, T=100, L=1, G=0.9, rS=1, rO=0, xi=1, nu=1e-2, dE=0.9, dL=0.9, dT=0.8, ID="Hill"):
		self.player = player
		self.ID = ID
		self.state = 0
		self.G = G
		self.E = E
		self.L = L
		self.T = T
		self.E0 = E
		self.L0 = L
		self.T0 = T
		self.dE = dE
		self.dL = dL
		self.dT = dT
		self.xi = xi
		self.nu = nu
		self.nS = nS
		self.nA = nA
		self.rS = rS  # weight for selfish reward
		self.rO = rO  # weight for prosocial reward
		self.Q = np.zeros((2+nS, nA))
		self.pi = np.ones((2+nS, nA)) / nA
		self.cSA = np.zeros((2+nS, nA))
		self.delta = np.zeros((2+nS, nA))
		self.V = np.zeros((2+nS))
	def act(self, money, history):
		self.setState(history, -1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.E:
			a = np.random.randint(0, money+1)
		elif self.T > 0:
			prob = softmax(self.pi[self.state] / self.T)
			a = np.where(np.cumsum(prob) >= np.random.rand())[0][0]
		else:
			a = np.argmax(self.pi[self.state])
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def learn(self, history):
		if self.player == "A":
			myGives = history['aGives']
			myRewards = history['aRewards']
			myStates = history['aStates']
			otherRewards = history['bRewards']
		else:
			myGives = history['bGives']
			myRewards = history['bRewards']
			myStates = history['bStates']
			otherRewards = history['aRewards']
		for t in range(len(myGives)-1):
			s = myStates[t]
			snew = myStates[t+1]
			a = myGives[t]
			r = (self.rS*myRewards[t]+self.rO*otherRewards[t])/(self.rS+self.rO)
			self.cSA[s,a] += 1
			# L = self.L / self.cSA[s,a]				
			L = self.L
			self.Q[s,a] += L * (r + self.G*np.max(self.Q[snew, :]) - self.Q[s, a])
			# Hill climbing policy update
			self.V[s] = np.sum(self.pi[s,:]*self.Q[s,:])
			for a in range(self.nA):
				if (1-self.pi[s,a]) == 0:
					self.delta[s,a] = (self.Q[s,a] - self.V[s])
				else:
					self.delta[s,a] = (self.Q[s,a] - self.V[s]) / (1-self.pi[s,a])
				# print(self.delta[s,a])
				delta = self.delta[s,a] - self.xi * np.abs(self.delta[s,a]) * self.pi[s,a]
				self.pi[s,a] += self.nu * delta
			self.pi[s] = softmax(self.pi[s])
	def restart(self):
		self.E = self.E0
		self.L = self.L0
		self.T = self.T0
		self.Q = np.zeros_like((self.Q))
		self.pi = np.zeros_like((self.pi))
		self.cSA = np.zeros_like(self.cSA)
		self.delta = np.zeros_like((self.delta))
		self.V = np.zeros_like((self.V))
	def reduceExploration(self, i):
		self.E *= self.dE
		self.L *= self.dL
		self.T *= self.dT
	def saveArchive(self, file):
		np.savez(file, Q=self.Q, pi=self.pi, nSA=self.cSA, delta=self.delta, V=self.V)
	def loadArchive(self, file):
		data = np.load(file)
		self.Q = data['Q']
		self.pi = data['pi']
		self.cSA = data['nSA']
		self.delta = data['delta']
		self.V = data['V']


class ModelBased(RLAgent):
	def __init__(self, player, nA, nS, E=0, T=100, G=0.9, rS=1, rO=0, dE=0.9, dT=0.9, ID="ModelBased"):
		self.player = player
		self.ID = ID
		self.state = 0
		self.G = G
		self.E = E
		self.T = T
		self.E0 = E
		self.T0 = T
		self.dE = dE
		self.dT = dT
		self.nS = nS
		self.nA = nA
		self.rS = rS  # weight for selfish reward
		self.rO = rO  # weight for prosocial reward
		self.R = np.zeros((2+nS, nA))
		self.M = np.zeros((2+nS, nA, 2+nS))
		self.V = np.zeros((2+nS))
		self.cSA = np.zeros((2+nS, nA))
		self.cSAS = np.zeros((2+nS, nA, 2+nS))
		self.pi = np.zeros((2+nS, nA))
	def act(self, money, history):
		self.setState(history, -1)
		if money == 0:
			a = 0
		elif np.random.rand() < self.E:
			a = np.random.randint(0, money+1)
		elif self.T > 0:
			prob = softmax(self.pi[self.state] / self.T)
			a = np.where(np.cumsum(prob) >= np.random.rand())[0][0]
		else:
			a = np.argmax(self.pi[self.state])
		give = int(np.clip(a, 0, money))
		keep = int(money - give)
		return give, keep
	def learn(self, history):
		if self.player == "A":
			myGives = history['aGives']
			myRewards = history['aRewards']
			myStates = history['aStates']
			otherRewards = history['bRewards']
		else:
			myGives = history['bGives']
			myRewards = history['bRewards']
			myStates = history['bStates']
			otherRewards = history['aRewards']
		for t in range(len(myGives)-1):
			s = myStates[t]
			snew = myStates[t+1]
			a = myGives[t]
			r = (self.rS*myRewards[t]+self.rO*otherRewards[t])/(self.rS+self.rO)
			self.cSA[s,a] += 1
			self.cSAS[s,a,snew] += 1
			self.M[s,a] = self.cSAS[s,a] / self.cSA[s,a]
			self.R[s,a] = (r + (self.cSA[s,a]-1) * self.R[s,a]) / self.cSA[s,a]
			nS = self.pi.shape[0]
			Mpi = np.zeros((nS, nS))
			Rpi = np.zeros((nS))
			for si in range(nS):
				# ai = int(self.pi[si])
				ai = int(np.argmax(self.pi[si]))
				Mpi[si] = self.M[si,ai]
				Rpi[si] = self.R[si,ai]
			self.V = np.linalg.solve(np.eye(nS)-self.G*Mpi, Rpi)
			# self.pi = np.argmax(self.R + self.G * (self.M @ self.V), axis=1)
			self.pi = self.R + self.G * (self.M @ self.V)
	def restart(self):
		self.E = self.E0
		self.T = self.T0
		self.R = np.zeros_like((self.R))
		self.M = np.zeros_like((self.M))
		self.V = np.zeros_like((self.V))
		self.cSA = np.zeros_like((self.cSA))
		self.cSAS = np.zeros_like((self.cSAS))
		self.pi = np.zeros_like((self.pi))
	def reduceExploration(self, i):
		self.E *= self.dE
		self.T *= self.dT
	def saveArchive(self, file):
		np.savez(file, R=self.R, T=self.M, V=self.V, nSA=self.cSA, nSAS=self.cSAS, pi=self.pi)
	def loadArchive(self, file):
		data = np.load(file)
		self.R = data['R']
		self.M = data['M']
		self.V = data['V']
		self.cSA = data['nSA']
		self.cSAS = data['nSAS']
		self.pi = data['pi']