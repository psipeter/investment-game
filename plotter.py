import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
sns.set(context='paper', style='white')


def plotTraining(rewards1, agent1, rewards2, agent2):
	fig, ax = plt.subplots()
	ax.plot(rewards1, label=str(agent1.ID)+str(agent1.player))
	ax.plot(rewards2, label=str(agent2.ID)+str(agent2.player))
	ax.set(xlabel="episode", ylabel="total reward")
	fig.legend()
	fig.savefig("plots/training_%s_%s.pdf"%(agent1.ID, agent2.ID))


def plotActions(agent1, agent2, env):
	gameName = agent1.ID + "_vs_" + agent2.ID
	kindestInvests = env.capital*np.ones(env.nIter)
	kindestReplies = env.matchFactor*np.ravel(agent1.myActions)
	actions1 = np.ravel(agent1.myActions)
	actions2 = np.ravel(agent2.myActions)
	fig, ax = plt.subplots()
	a = ax.plot(actions1, label=str(agent1.ID)+"-"+str(agent1.player))
	# ax.plot(kindestInvests, label='kindest investment', alpha=0.5, color=a[0].get_color())
	b = ax.plot(actions2, label=str(agent2.ID)+"-"+str(agent2.player))
	# ax.plot(kindestReplies, label='kindest reply', alpha=0.5, color=b[0].get_color())
	ax.set(xlabel="iteration", ylabel="action", xlim=((-env.nIter/100, env.nIter)), ylim=((0, env.capital*env.matchFactor)))
	fig.legend()
	sns.despine()
	fig.savefig("plots/"+gameName+"_actions.pdf")
	return

def plotRewards(agent1, agent2, env):
	gameName = agent1.ID + "_vs_" + agent2.ID
	sum1 = np.mean(agent1.rewards)
	sum2 = np.mean(agent2.rewards)
	winnerIdx = np.argmax([sum1, sum2])
	winner = np.array([agent1, agent2])[winnerIdx].ID
	rewards1 = np.ravel(agent1.rewards)
	rewards2 = np.ravel(agent2.rewards)
	fig, ax = plt.subplots()
	ax.plot(rewards1, label=str(agent1.ID)+"-"+str(agent1.player))
	ax.plot(rewards2, label=str(agent2.ID)+"-"+str(agent2.player))
	ax.set(xlabel="iteration", ylabel="reward",
		title="winner: %s (%.1f/%.1f)"%(winner, sum1, sum2),
		xlim=((-env.nIter/100, env.nIter)), ylim=((-1, env.capital*env.matchFactor)))
	fig.legend()
	sns.despine()
	fig.savefig("plots/"+gameName+"_rewards.pdf")

def plotPerformance(agent, pop, env, learners, plotOther=False):
	print("plotting...")
	columns = ("agent2", "nAvg", "nEps", "reward", "player", "who")
	dfs = []
	for agent2 in pop:
		rewardsInvestorA = np.load("data/%s_vs_%s%s.npz"%(agent.ID, agent2.ID, learners))['rewardsInvestorA']
		rewardsInvestorB = np.load("data/%s_vs_%s%s.npz"%(agent.ID, agent2.ID, learners))['rewardsInvestorB']
		rewardsReturnerA = np.load("data/%s_vs_%s%s.npz"%(agent.ID, agent2.ID, learners))['rewardsReturnerA']
		rewardsReturnerB = np.load("data/%s_vs_%s%s.npz"%(agent.ID, agent2.ID, learners))['rewardsReturnerB']
		for a in range(rewardsInvestorA.shape[0]):
			for e in range(rewardsInvestorA.shape[1]):
				dfs.append(pd.DataFrame([[agent2.ID, a, e, rewardsInvestorA[a,e], "A", "self"]], columns=columns))
				dfs.append(pd.DataFrame([[agent2.ID, a, e, rewardsInvestorB[a,e], "A", "other"]], columns=columns))
				dfs.append(pd.DataFrame([[agent2.ID, a, e, rewardsReturnerA[a,e], "B", "self"]], columns=columns))
				dfs.append(pd.DataFrame([[agent2.ID, a, e, rewardsReturnerB[a,e], "B", "other"]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)

	ylim = env.capital*env.matchFactor
	finalEp = rewardsInvestorA.shape[1] - 1
	fig, axs = plt.subplots(ncols=len(pop), nrows=1, figsize=(len(pop)*2, 2), sharey=True)
	for a2 in range(len(pop)):
		agent2 = pop[a2]
		a2ID = agent2.ID
		ax = axs[a2] if len(pop) > 1 else axs
		sns.lineplot(data=df.query('agent2 == @a2ID'), x="nEps", y="reward", hue="player", style="who", ax=ax)
		ax.set(xlabel=None, ylim=((0, ylim)), xticks=(([0, finalEp+1])), yticks=(([0, 5, 10, 15, 20, 25, 30])), title=a2ID)
		if a2 == 0:
			ax.set(ylabel=agent.ID)
		ax.grid(True, axis='y')
		leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
		# if a2 == 0:
		leg.remove()
	fig.tight_layout()
	fig.savefig("plots/performance_training_%s%s.pdf"%(agent.ID, "_learners" if learners else ""))
	# fig.savefig("plots/performance_training_%s.svg"%agent.ID)

	# playa = "self"
	# dfFinal = df.query("nEps == @finalEp") if plotOther else df.query("nEps == @finalEp & who == @playa")
	# fig, ax = plt.subplots(figsize=((16, 8)))
	# if plotOther:
	# 	g = sns.catplot(data=dfFinal, x="agent2", y="reward", hue="player", col="who", kind="bar")
	# else:
	# 	sns.barplot(data=dfFinal, x="agent2", y="reward", hue="player", ax=ax)
	# ax.set(ylim=((0, ylim)), yticks=(([0, 5, 10, 15, 20, 25, 30])), title=agent.ID)
	# ax.grid(True, axis='y')
	# fig.tight_layout()
	# fig.savefig("plots/performance_barplot_%s%s.pdf"%(agent.ID, "_learners" if learners else ""))
	# fig.savefig("plots/performance_final_%s.svg"%agent.ID)	


def plotRecovery(agent1, agent2, env, rewards1, rewards2, rewards3, rewards4, alpha1, alpha2):
	print("plotting...")
	columns = ("nAvg", "nEps", "reward", "player", "alpha")  # "who", 
	dfs = []
	for a in range(rewards1.shape[0]):
		for e in range(rewards1.shape[1]):
			dfs.append(pd.DataFrame([[a, e, rewards1[a,e], "A", alpha1]], columns=columns))  # "self", 
			dfs.append(pd.DataFrame([[a, e, rewards2[a,e], "B", alpha1]], columns=columns))  # "other", 
			dfs.append(pd.DataFrame([[a, e, rewards3[a,e], "A", alpha2]], columns=columns))  # "self", 
			dfs.append(pd.DataFrame([[a, e, rewards4[a,e], "B", alpha2]], columns=columns))  # "other", 
	df = pd.concat([df for df in dfs], ignore_index=True)

	ylim = env.capital*env.matchFactor
	finalEp = df["nEps"].max()
	fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((10, 2)), sharey=True)
	dfA = df.query("alpha == @alpha1")
	dfB = df.query("alpha == @alpha2")
	sns.lineplot(data=dfA, x="nEps", y="reward", hue="player", ax=ax1)  # , style="who"
	sns.lineplot(data=dfB, x="nEps", y="reward", hue="player", ax=ax2)  # , style="who"
	ax1.set(xlabel="episode", ylabel="reward", xticks=(([0, finalEp+1])),
		ylim=((0, ylim)), yticks=(([0, 5, 10, 15, 20, 25, 30])),
		title=r"$\alpha^A$=%s, "%alpha1 + r"$\alpha^B$=%s"%alpha1)
	ax2.set(xlabel="episode", ylabel=None, xticks=(([0, finalEp+1])),
		ylim=((0, ylim)), yticks=(([0, 5, 10, 15, 20, 25, 30])),
		title=r"$\alpha^A$=%s, "%alpha2 + r"$\alpha^B$=%s"%alpha1)
	ax1.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg1 = ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	leg2 = ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	leg1.remove()
	leg2.remove()
	fig.tight_layout()
	fig.savefig("plots/plotRecovery_%s_%s.pdf"%(agent1.ID, agent2.ID))




def plotTournament(pop, df, env):
	print("plotting...")
	finalRound = df["round"].max() + 1
	ylim_zoom = ((5, 20))
	ylim = ((0, env.capital*env.matchFactor))
	figsize = (6, 2)
	hue_order = [agent.ID for agent in pop]

	for agent1 in pop:
		a1ID = agent1.ID
		dfA = df.query("agent1 == @a1ID & player == 'A'")
		dfB = df.query("agent1 == @a1ID & player == 'B'")
		fig, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=figsize, sharey=True)
		sns.lineplot(data=dfA, x="round", y="reward", hue="agent2", ax=ax1, hue_order=hue_order)
		sns.lineplot(data=dfB, x="round", y="reward", hue="agent2", ax=ax2, hue_order=hue_order)
		ax1.set(xlabel=None, ylim=ylim, xticks=(([0, finalRound])),
			yticks=(([0, 5, 10, 15, 20, 25, 30])), ylabel=a1ID, title="role A")
		ax2.set(xlabel=None, ylim=ylim, xticks=(([0, finalRound])),
			yticks=(([0, 5, 10, 15, 20, 25, 30])), ylabel=a1ID, title="role B")
		ax1.grid(True, axis='y')
		ax2.grid(True, axis='y')
		leg1 = ax1.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))
		leg2 = ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))
		leg1.remove()
		# leg1 = ax1.legend(loc='upper left') #, bbox_to_anchor=(1, 0.5))
		# leg2 = ax2.legend(loc='upper left') #, bbox_to_anchor=(1, 0.5))
		# leg2.remove()
		fig.tight_layout()
		fig.savefig("plots/tournament_%s.pdf"%a1ID)

	dfA = df.query("player == 'A'")
	dfB = df.query("player == 'B'")
	fig, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=figsize, sharey=True)
	sns.lineplot(data=dfA, x="round", y="reward", hue="agent1", ax=ax1, hue_order=hue_order)
	sns.lineplot(data=dfB, x="round", y="reward", hue="agent1", ax=ax2, hue_order=hue_order)
	ax1.set(xlabel=None, ylim=ylim_zoom, xticks=(([0, finalRound])),
		yticks=(([5, 10, 15, 20])), title="role A")
	ax2.set(xlabel=None, ylim=ylim_zoom, xticks=(([0, finalRound])),
		yticks=(([5, 10, 15, 20])), title="role B")
	ax1.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg1 = ax1.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))
	leg2 = ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))
	leg1.remove()
	# leg1 = ax1.legend(loc='upper left') #, bbox_to_anchor=(1, 0.5))
	# leg2 = ax2.legend(loc='upper left') #, bbox_to_anchor=(1, 0.5))
	# leg2.remove()
	fig.tight_layout()
	fig.savefig("plots/tournament_all.pdf")

	# finalRound = df["round"].max()	
	# fig, ax = plt.subplots(figsize=((16, 8)))
	# for a1 in range(len(learnPop)):
	# 	agent1 = learnPop[a1]
	# 	a1ID = agent1.ID
	# 	# result = df.groupby(["agent1"])['reward'].aggregate(np.mean).reset_index().sort_values('reward') # chart order
	# 	dfFinal = df.query('round == @finalRound & agent1 == @a1ID')
	# 	sns.barplot(data=dfFinal, x='agent2', y='reward', hue="player")  # , order=result['agent1']
	# 	ax.set(xlabel=None, ylim=((0, ylim)), yticks=(([0, 10, 20, 30])), title=a1ID)
	# 	ax.grid(True, axis='y')
	# 	fig.savefig("plots/tournament_barplot_%s.pdf"%a1ID)
	# 	# fig.savefig("plots/tournament_%s_barplot.svg"%title)
