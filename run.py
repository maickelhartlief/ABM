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
import seaborn as sns

## import parameter configuration from file (default: configs.normal)
params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))

## create network
if params.network == 'fully_connected':
    graph = nx.complete_graph(n = params.n_agents)
elif params.network == 'ba':
    graph = nx.barabasi_albert_graph(n = params.n_agents, m = params.m_barabasi)

## create model
model = Party_model(prob_stimulus = params.prob_stimulus,
              prob_interaction = params.prob_interaction,
              prob_move = params.prob_move,
              prob_friend = params.prob_friend,
              until_eligible = params.until_eligible,
              characteristics_affected = params.characteristics_affected,
              edges_per_step = params.edges_per_step,
              n_agents = params.n_agents,
              network = 'barabasi',
              m_barabasi = params.m_barabasi,
              fermi_alpha = params.fermi_alpha,
              fermi_b = params.fermi_b
              )


## create agents
# generate random starting characteristics, based on desired distribution
if params.char_distr == 'normal': # truncated normal distribution, to stay within limits
    mu = 2
    distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
    samples = distr.rvs(params.n_agents * 8)
    characteristics = np.reshape(samples, (params.n_agents, 8))
elif params.char_distr == 'uniform': # uniform distribution within limits
    characteristics = np.random.uniform(1, 5, (params.n_agents, 8))

# intialize each agent
for idx in range(params.n_agents):
    model.add_agent(Member(idx,
                           model,
                           # NOTE: This was a flat 20% probability, butit is more natural to make this chance related to prob_move.
                           until_eligible = 0 if random.uniform(0, 1) < params.prob_move else params.until_eligible,
                           vote_duty = random.uniform(0, 1) < .03,
                           active = characteristics[idx, 0],
                           overt = characteristics[idx, 1],
                           autonomous = characteristics[idx, 2],
                           approaching = characteristics[idx, 3],
                           continuous = characteristics[idx, 4],
                           outtaking = characteristics[idx, 5],
                           expressive = characteristics[idx, 6],
                           social = characteristics[idx, 7],
                           ses = random.randint(1, 3)))


## run simulation

# for i in range(1000):
#     model.step()
# #print(model.p_accept_list)
# nx.draw(model.graph)
# plt.show()

# plt.hist(model.p_accept_list)
# plt.show()


#
for iteration in range(params.n_iterations):
    model.step()
    '''
    smith = model.agents[0]
    print(f'active = {round(smith.active, 1)}\n'
          f'overt  = {round(smith.overt, 1)}\n'
          f'autonomous  = {round(smith.autonomous, 1)}\n'
          f'approaching  = {round(smith.approaching, 1)}\n'
          f'continuous  = {round(smith.continuous, 1)}\n'
          f'outtaking  = {round(smith.outtaking, 1)}\n'
          f'expressive  = {round(smith.expressive, 1)}\n'
          f'social  = {round(smith.social, 1)}\n'
          f'ses  = {smith.ses}\n')
    print(f'pp = {smith.pps}')
    '''

agent_data = model.datacollector.get_agent_vars_dataframe()
model_data = model.datacollector.get_model_vars_dataframe()


## visualize results
result_path = 'results'
if not os.path.exists(result_path):
   os.makedirs(result_path)
result_path += '/'

# plots network structure
nx.draw(model.graph)
plt.savefig(result_path + 'network.png')
plt.clf()

# plot the number of voters over time
sns.lineplot(data = model_data,
             x = model_data.index,
             y = 'voters')
plt.savefig(result_path + 'voters.png')
plt.clf()

# plot the mean political participation over time
sns.lineplot(data = agent_data.groupby("Step").mean(),
             x = 'Step',
             y = 'political participation')
plt.savefig(result_path + 'mean_pp.png')
plt.clf()

# plot number of agents with certain level of political participation over time
for pp in range(13):
    sns.lineplot(data = agent_data[agent_data["political participation"] == pp].groupby("Step").count(),
                 x = 'Step',
                 y = 'political participation',
                 label = pp)

plt.legend()
plt.savefig(result_path + 'agents_per_pp.png')
plt.clf()

# # plot number of agents within certain ranges of political participation over time
# # NOTE: this is an aggregated version of the previous, like in the base model
pps_aggr = [ agent_data["political participation"] == 0,
         (agent_data["political participation"] > 0) & (agent_data["political participation"] < 5),
         (agent_data["political participation"] >= 5) & (agent_data["political participation"] <= 7),
         agent_data["political participation"] >= 8 ]
labels = ['Apathetic (0)', 'Spectators (1-4)', 'Transitionals (5-7)', 'Gladiators (8-12)']
colors = ['tan', 'orange', 'pink', 'red']
for pps, label, color in zip(pps_aggr, labels, colors):
    sns.lineplot(data = agent_data[pps].groupby("Step").count(),
                 x = 'Step',
                 y = 'political participation',
                 label = label,
                 color = color)
plt.legend()
plt.savefig(result_path + 'agents_per_pp_aggr.png')
plt.clf()
