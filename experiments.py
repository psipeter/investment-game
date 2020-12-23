import numpy as np
try:
	from utils import *
	from agents import *
	from plotter import *
except:
	from .utils import *
	from .agents import *
	from .plotter import *

''' one-on-one matchups '''

env = Env(nIter=100, capital=10, matchFactor=3)

a1 = FMQ(env)
a2 = WoLFPHC(env)
a3 = PGAAPP(env)
a4 = ModelBased(env)

b1 = Gaussian(mean=0.0, std=0.1, ID="Greedy")
b2 = Gaussian(mean=1.0, std=0.1, ID="Generous")
b3 = Accumulator(env, maxReturn=0.5)
b4 = TitForTat(env)

c1 = FMQ(env)
c2 = WoLFPHC(env)
c3 = PGAAPP(env)
c4 = ModelBased(env)

# nonlearners = [b1, b2, b3, b4]
# learners = [c1, c2, c3, c4]
# performance(a1, nonlearners, env, nAvg=3, nEps=100, learners=False, plotOther=True)
# performance(a1, learners, env, nAvg=3, nEps=100, learners=True, plotOther=True)
# performance(a2, nonlearners, env, nAvg=3, nEps=100, learners=False, plotOther=True)
# performance(a2, learners, env, nAvg=3, nEps=100, learners=True, plotOther=True)
# performance(a3, nonlearners, env, nAvg=3, nEps=100, learners=False, plotOther=True)
# performance(a3, learners, env, nAvg=3, nEps=100, learners=True, plotOther=True)
# performance(a4, nonlearners, env, nAvg=3, nEps=100, learners=False, plotOther=True)
# performance(a4, learners, env, nAvg=3, nEps=100, learners=True, plotOther=True)

# a1.loadModel()
# performance(a1, [b1, b2, b3, b4], env, nAvg=3, nEps=100, learners=False, plotOther=True)



''' tournament '''

env = Env(nIter=5, capital=10, matchFactor=3)

pop = [
	FMQ(env, alpha=3e-3, decay=0.99),
	PGAAPP(env, alpha=3e-3, nu=1e-3, decay=0.99),
	WoLFPHC(env, alpha=3e-3, deltaW=3, deltaL=1, decay=0.99),
	ModelBased(env, decay=0.99, updateFreq=1),
	Accumulator(env, maxReturn=0.5),
	TitForTat(env),
	Gaussian(mean=0.0, std=0.1, ID="Greedy"),
	Gaussian(mean=1.0, std=0.1, ID="Generous"),
]

tournament(pop, env, nAvg=3, nRounds=300)

# pop[0].saveModel(learnVsHumans=True)
# pop[1].saveModel(learnVsHumans=True)
# pop[2].saveModel(learnVsHumans=True)

