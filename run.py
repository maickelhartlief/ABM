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
import pandas as pd

## import parameter configuration from file (default: configs.normal)
params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))

for network in params.networks:
    print(f"simulating a {network.replace('_', ' ')} network")
    agent_data = pd.DataFrame()
    model_data = pd.DataFrame()
    for run in range(params.n_runs):
        print(f'run {run + 1} / {params.n_runs}', end = '\r', flush = True)
        ## create model
        model = Party_model(prob_stimulus = params.prob_stimulus,
                            prob_interaction = params.prob_interaction,
                            prob_move = params.prob_move,
                            prob_link = params.prob_link,
                            until_eligible = params.until_eligible,
                            characteristics_affected = params.characteristics_affected,
                            network = network,
                            edges_per_step = params.edges_per_step,
                            n_agents = params.n_agents,
                            m_barabasi = params.m_barabasi,
                            fermi_alpha = params.fermi_alpha,
                            fermi_b = params.fermi_b)

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
                                   until_eligible = 0 if random.uniform(0, 1) > params.prob_move else params.until_eligible,
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

        # run model
        for iteration in range(params.n_iterations):
            model.step()
        
        run_model_data = model.datacollector.get_model_vars_dataframe()
        run_agent_data = model.datacollector.get_agent_vars_dataframe()

        run_model_data = run_model_data.reset_index().rename(columns = {'index' : 'Step'})
        run_model_data['run'] = run

        run_agent_data = run_agent_data.reset_index()
        run_agent_data['run'] = run

        agent_data = pd.concat([agent_data, run_agent_data], ignore_index = True)
        model_data = pd.concat([model_data, run_model_data], ignore_index = True)

    print('saving results ...', end = '\r', flush = True)
    ## Average data over runs
    #model_data = model_data.groupby('iteration').agg(['mean', 'std']).drop(columns = ['run'])
    #agent_data = agent_data.groupby(['Step', 'AgentID']).agg(['mean', 'std']).drop(columns = ['run'])
    
    ## visualize results
    # set location
    result_path = 'results/' + network
    if not os.path.exists(result_path):
       os.makedirs(result_path)
    result_path += '/'

    # plots network structure
    nx.draw(model.graph, node_size = 10)
    plt.savefig(f"{result_path}network_{model.network}.png")
    plt.clf()

    # plot the number of voters over time
    sns.lineplot(data = model_data,
                 x = 'Step',
                 y = 'voters',
                 errorbar = 'sd')
    plt.ylim(0, 100)
    plt.savefig(f"{result_path}{model.network}_voters.png")
    plt.clf()

    # plot the mean political participation over time
    sns.lineplot(data = agent_data,
                 x = 'Step',
                 y = 'political participation',
                 errorbar = 'sd')
    plt.ylim(0,12)
    plt.savefig(f"{result_path}{model.network}_mean_pp.png")
    plt.clf()

    # plot number of agents with certain level of political participation over time
    for pp in range(13):
        #print(agent_data[agent_data["political participation"] == pp].groupby(['Step', 'run']).count())
        sns.lineplot(data = agent_data[agent_data["political participation"] == pp].groupby(['Step', 'run']).count(),
                     x = 'Step',
                     y = 'political participation',
                     errorbar = 'sd',
                     label = pp)
    plt.ylabel('count')
    plt.legend()
    plt.savefig(f"{result_path}{model.network}_agents_per_pp.png")
    plt.clf()

    # plot number of agents within certain ranges of political participation over time
    # NOTE: this is an aggregated version of the previous, like in the base model
    pps_aggr = [ agent_data["political participation"] == 0,
             (agent_data["political participation"] > 0) & (agent_data["political participation"] < 5),
             (agent_data["political participation"] >= 5) & (agent_data["political participation"] <= 7),
             agent_data["political participation"] >= 8 ]
    labels = ['Apathetic (0)', 'Spectators (1-4)', 'Transitionals (5-7)', 'Gladiators (8-12)']
    colors = ['tan', 'orange', 'pink', 'red']
    for pps, label, color in zip(pps_aggr, labels, colors):
        sns.lineplot(data = agent_data[pps].groupby(['Step', 'run']).count(),
                     x = 'Step',
                     y = 'political participation',
                     errorbar = 'sd',
                     label = label,
                     color = color)
    plt.ylabel('count')
    plt.legend()
    plt.savefig(f"{result_path}agents_per_pp_aggr_network_{model.network}.png")
    plt.clf()

    # saves numerical results
    pp = (agent_data.groupby(['Step', 'political participation']).count()['AgentID'] / params.n_runs).reset_index()
    pp = pp[pp['Step'] >= params.n_iterations - 100].groupby('political participation').mean().reset_index()[['political participation', 'AgentID']]
    with open(result_path + model.network, 'w') as file:
        file.write(model_data.groupby('Step').mean()['voters'].iloc[-1000:-1].to_string(header=False, index=False) + '\n')
        
        file.write(f"Apathetic: {pp[pp['political participation'] == 0]['AgentID'].sum()}\n")
        file.write(f"Spectators: {pp[(pp['political participation'] > 0) & (pp['political participation'] <= 4)]['AgentID'].sum()}\n")
        file.write(f"Transitionals: {pp[(pp['political participation'] > 4) & (pp['political participation'] <= 7)]['AgentID'].sum()}\n")
        file.write(f"Gladiators: {pp[pp['political participation'] > 7]['AgentID'].sum()}\n")

print('Done!                ', end = '\r', flush = True)
