import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import time


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



def plotForgivenessFriendliness(df, capital, match):
	dfMeanA = df.drop(columns=['meanB', 'stdA', 'stdB']).set_index(['F', 'rO'])
	dfMeanB = df.drop(columns=['meanA', 'stdA', 'stdB']).set_index(['F', 'rO'])
	dfStdA = df.drop(columns=['meanA', 'meanB', 'stdB']).set_index(['F', 'rO'])
	dfStdB = df.drop(columns=['meanA', 'meanB', 'stdA']).set_index(['F', 'rO'])
	tableMeanA = dfMeanA.unstack(level=0)
	tableMeanB = dfMeanB.unstack(level=0)
	tableStdA = dfStdA.unstack(level=0)
	tableStdB = dfStdB.unstack(level=0)

	xticks = np.array(df.set_index(['F', 'rO']).unstack(level=0).index)
	yticks = np.array(df.set_index(['rO', 'F']).unstack(level=0).index)
	rx = (xticks[1]-xticks[0])/2
	ry = (yticks[1]-yticks[0])/2
	viridis = plt.get_cmap('viridis', 256)

	# normalize mean and std 0 to 1
	A = np.array(tableMeanA) / (capital*match)
	B = 1 - np.array(tableStdA) / (capital*match/2)
	# convert means to RGB spectrum and set alpha equal to std
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	plt.xlabel("Agent Friendliness")
	plt.ylabel("T4T Forgiveness")
	plt.title("T4T Rewards")
	fig.savefig("plots/ForgivenessFriendliness_meanT4T.pdf")

	A = np.array(tableMeanB) / (capital*match)
	B = 1 - np.array(tableStdB) / (capital*match/2)
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	plt.xlabel("Agent Friendliness")
	plt.ylabel("T4T Forgiveness")
	plt.title("Agent Rewards")
	fig.savefig("plots/ForgivenessFriendliness_meanAgent.pdf")


def plotFriendlinessFriendliness(df, capital, match):
	dfMeanA = df.drop(columns=['meanB', 'stdA', 'stdB']).set_index(['rOA', 'rOB'])
	dfMeanB = df.drop(columns=['meanA', 'stdA', 'stdB']).set_index(['rOA', 'rOB'])
	dfStdA = df.drop(columns=['meanA', 'meanB', 'stdB']).set_index(['rOA', 'rOB'])
	dfStdB = df.drop(columns=['meanA', 'meanB', 'stdA']).set_index(['rOA', 'rOB'])
	tableMeanA = dfMeanA.unstack(level=0)
	tableMeanB = dfMeanB.unstack(level=0)
	tableStdA = dfStdA.unstack(level=0)
	tableStdB = dfStdB.unstack(level=0)

	xticks = np.array(df.set_index(['rOA', 'rOB']).unstack(level=0).index)
	yticks = np.array(df.set_index(['rOB', 'rOA']).unstack(level=0).index)
	rx = (xticks[1]-xticks[0])/2
	ry = (yticks[1]-yticks[0])/2
	viridis = plt.get_cmap('viridis', 256)

	# normalize mean and std 0 to 1
	A = np.array(tableMeanA) / (capital*match)
	B = 1 - np.array(tableStdA) / (capital*match/2)
	# convert means to RGB spectrum and set alpha equal to std
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	plt.xlabel("Agent B Friendliness")
	plt.ylabel("Agent A Friendliness")
	plt.title("Agent A Rewards")
	fig.savefig("plots/FriendlinessFriendliness_A.pdf")

	A = np.array(tableMeanB) / (capital*match)
	B = 1 - np.array(tableStdB) / (capital*match/2)
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	plt.xlabel("Agent B Friendliness")
	plt.ylabel("Agent A Friendliness")
	plt.title("Agent B Rewards")
	fig.savefig("plots/FriendlinessFriendliness_B.pdf")



# def plotForgiveness2D(df):
# 	dfMeanA = df.drop(columns=['meanB', 'stdA', 'stdB']).set_index(['FA', 'FB'])
# 	dfMeanB = df.drop(columns=['meanA', 'stdA', 'stdB']).set_index(['FA', 'FB'])
# 	dfStdA = df.drop(columns=['meanA', 'meanB', 'stdB']).set_index(['FA', 'FB'])
# 	dfStdB = df.drop(columns=['meanB', 'meanB', 'stdA']).set_index(['FA', 'FB'])
# 	tableMeanA = dfMeanA.unstack(level=0)
# 	tableMeanB = dfMeanB.unstack(level=0)
# 	tableStdA = dfStdA.unstack(level=0)
# 	tableStdB = dfStdB.unstack(level=0)

# 	xticks = np.array(df.set_index(['FB', 'FA']).unstack(level=0).index)
# 	yticks = np.array(df.set_index(['FA', 'FB']).unstack(level=0).index)
# 	rx = (xticks[1]-xticks[0])/2
# 	ry = (yticks[1]-yticks[0])/2


# 	fig, ax = plt.subplots()
# 	# sns.heatmap(tableMeanA, cmap='viridis')  # breaks ticks and labels
# 	c = ax.imshow(np.array(tableMeanA),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("T4T B Forgiveness")
# 	plt.ylabel("T4T A Forgiveness")
# 	plt.title("Mean A Rewards")
# 	fig.savefig("plots/forgiveness2d_meanA.pdf")

# 	fig, ax = plt.subplots()
# 	c = ax.imshow(np.array(tableMeanB),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("T4T B Forgiveness")
# 	plt.ylabel("T4T A Forgiveness")
# 	plt.title("Mean B Rewards")
# 	fig.savefig("plots/forgiveness2d_meanB.pdf")

# 	fig, ax = plt.subplots()
# 	c = ax.imshow(np.array(tableStdA),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("T4T B Forgiveness")
# 	plt.ylabel("T4T A Forgiveness")
# 	plt.title("Std A Rewards")
# 	fig.savefig("plots/forgiveness2d_stdA.pdf")

# 	fig, ax = plt.subplots()
# 	c = ax.imshow(np.array(tableStdB),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("T4T B Forgiveness")
# 	plt.ylabel("T4T A Forgiveness")
# 	plt.title("Std B Rewards")
# 	fig.savefig("plots/forgiveness2d_stdB.pdf")


# def plotFriendliness2D(df):
# 	dfMeanA = df.drop(columns=['meanB', 'stdA', 'stdB']).set_index(['rOA', 'rOB'])
# 	dfMeanB = df.drop(columns=['meanA', 'stdA', 'stdB']).set_index(['rOA', 'rOB'])
# 	dfStdA = df.drop(columns=['meanA', 'meanB', 'stdB']).set_index(['rOA', 'rOB'])
# 	dfStdB = df.drop(columns=['meanB', 'meanB', 'stdA']).set_index(['rOA', 'rOB'])
# 	tableMeanA = dfMeanA.unstack(level=0)
# 	tableMeanB = dfMeanB.unstack(level=0)
# 	tableStdA = dfStdA.unstack(level=0)
# 	tableStdB = dfStdB.unstack(level=0)

# 	xticks = np.array(df.set_index(['rOB', 'rOA']).unstack(level=0).index)
# 	yticks = np.array(df.set_index(['rOA', 'rOB']).unstack(level=0).index)
# 	rx = (xticks[1]-xticks[0])/2
# 	ry = (yticks[1]-yticks[0])/2


# 	fig, ax = plt.subplots()
# 	# sns.heatmap(tableMeanA, cmap='viridis')  # breaks ticks and labels
# 	c = ax.imshow(np.array(tableMeanA),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("RL B Friendliness")
# 	plt.ylabel("RL A Friendliness")
# 	plt.title("Mean A Rewards")
# 	fig.savefig("plots/friendliness2d_meanA.pdf")

# 	fig, ax = plt.subplots()
# 	c = ax.imshow(np.array(tableMeanB),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("RL B Friendliness")
# 	plt.ylabel("RL A Friendliness")
# 	plt.title("Mean B Rewards")
# 	fig.savefig("plots/friendliness2d_meanB.pdf")

# 	fig, ax = plt.subplots()
# 	c = ax.imshow(np.array(tableStdA),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("RL B Friendliness")
# 	plt.ylabel("RL A Friendliness")
# 	plt.title("Std A Rewards")
# 	fig.savefig("plots/friendliness2d_stdA.pdf")

# 	fig, ax = plt.subplots()
# 	c = ax.imshow(np.array(tableStdB),
# 		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
# 		interpolation='nearest',
# 		cmap='viridis')
# 	ax.set_aspect('auto')
# 	plt.colorbar(c)
# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	plt.xlabel("RL B Friendliness")
# 	plt.ylabel("RL A Friendliness")
# 	plt.title("Std B Rewards")
# 	fig.savefig("plots/friendliness2d_stdB.pdf")

