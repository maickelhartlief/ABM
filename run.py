###### run.py
# Runs the model for a certain number of runs and iterations, and for all network 
# types specified in the config function (config/normal.py by default)
####

# Internal imports
from party import Party_model
from agents import Member

# External imports
import sys
import os
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from importlib import import_module
from mesa import Agent, Model, space, time
from mesa.datacollection import DataCollector
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
                            params = params,
                            network = network)

        # run model
        for iteration in range(params.n_iterations):
            model.step()

        def safe_run_data(data, run_data):
            run_data = run_data.reset_index().rename(columns = {'index' : 'Step'})
            run_data['run'] = run
            return pd.concat([data, run_data], ignore_index = True)

        agent_data = safe_run_data(agent_data, model.datacollector.get_agent_vars_dataframe())
        model_data = safe_run_data(model_data, model.datacollector.get_model_vars_dataframe())
        
    print(agent_data)
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

    pps_dict = {}
    category_dict = {}
    for node in model.graph.nodes:
        pps = node.pps
        if pps == 0:
            category_dict[node] = 0
        elif pps >= 1 and pps <= 4:
            category_dict[node] = 1
        elif pps >= 5 and pps <=7:
            category_dict[node] = 2
        else:
            category_dict[node] = 3
        pps_dict[node] = node.pps

    # set location
    result_path = 'results/networks'
    if not os.path.exists(result_path):
       os.makedirs(result_path)
    result_path += '/'

    nx.set_node_attributes(model.graph, pps_dict, 'pps')
    nx.set_node_attributes(model.graph, category_dict, 'cat')
    nx.write_graphml(model.graph, f'{result_path}{network}.graphml')

print('Done!                ', end = '\r', flush = True)
