# internal imports
from party import Party_model
from agents import Member

# external imports
import sys
import os
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from importlib import import_module
from mesa import Agent, Model, space, time, DataCollector
import networkx as nx

## import parameter configuration from file (default: configs.normal)
params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))


## create model
model = Party_model(prob_stimulus = params.prob_stimulus,
              prob_interaction = params.prob_interaction,
              prob_move = params.prob_move,
              until_eligible = params.until_eligible,
              characteristics_affected = params.characteristics_affected,
              n_agents = params.n_agents,
              m_barabasi = params.node_connections,
              )


## create agents
# generate random starting characteristics, based on desired distribution
if params.char_distr == 'normal': # truncated normal distribution, to stay within limits
    mu = 2
    distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
    samples = distr.rvs(params.n_agents * 8)
    characteristics = np.reshape(samples, (params.n_agents, 8))
elif params.char_distr == 'uniform': # uniform distribution within limits
    characteristics = np.random.uniform(0, 5, (params.n_agents, 8))

# intialize each agent
for idx in range(params.n_agents):
    model.add_agent(Member(idx,
                          model,
                          # TODO: would be more natural to make this chance related to prob_move.
                          until_eligible = 0 if random.uniform(0, 1) < .8 else params.until_eligible,
                          vote_duty = random.uniform(0, 1) < .03,
                          active = characteristics[idx, 0],
                          overt = characteristics[idx, 1],
                          autonomous = characteristics[idx, 2],
                          approaching = characteristics[idx, 3],
                          continuous = characteristics[idx, 4],
                          outtaking = characteristics[idx, 5],
                          expressive = characteristics[idx, 6],
                          social = characteristics[idx, 7],
                          ses = random.uniform(1, 3)))


## run simulation

model.step()
nx.draw(model.graph)
plt.show()
# for iteration in range(params.n_iterations):
#     model.step()

df = model.datacollector.get_agent_vars_dataframe()

#
## visualize results
result_path = 'results'
if not os.path.exists(result_path):
   os.makedirs(result_path)
result_path += '/'


plt.plot(df.groupby("Step").mean())
plt.savefig(result_path + 'mean_pp.png')
plt.clf()

#plot number of agents with certain level of political participation over time
for pp in range(13):
    plt.plot((df[df["PPS"] == pp]).groupby("Step").count(), label = pp)

plt.legend()
plt.savefig(result_path + 'agents_per_pp.png')
plt.clf()

# # plot number of agents within certain ranges of political participation over time
# # NOTE: this is an aggregated version of the previous, like in the base model
plt.plot((df[df["PPS"] == 0]).groupby("Step").count(), label = 'Apathetic (0)',
         color = 'tan')
plt.plot((df[(df["PPS"] > 0) & (df["PPS"] < 5)]).groupby("Step").count(), label = 'Spectators (1-4)', color ='orange')
plt.plot((df[(df["PPS"] >= 5) & (df["PPS"] <= 7)]).groupby("Step").count(), label = 'Transitionals (5-7)', color ='pink')
plt.plot((df[df["PPS"] >= 8]).groupby("Step").count(), label = 'Gladiators (8-12)', color ='red')
plt.legend()

plt.savefig(result_path + 'agents_per_pp_aggr.png')
plt.clf()
