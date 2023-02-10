###### run.py
# Runs the model for a certain number of runs and iterations, and for all network 
# types specified in the config function (config/normal.py by default)
####

# Internal imports
from party import Party_model
from agents import Member
from utils import safe_run_data, make_path, get_config, get_category

# External imports
import sys
import os
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from mesa import Agent, Model, space, time
from mesa.datacollection import DataCollector
import networkx as nx
import seaborn as sns
import pandas as pd


# Import parameter configuration from file based on input argument 
# (default: configs.normal)
params = get_config()

# Run model with each network structure
for network in params.networks:
    print(f"simulating a {network.replace('_', ' ')} network")

    # Initialize data
    agent_data = pd.DataFrame()
    model_data = pd.DataFrame()
    
    # Perform independent runs of the model
    for run in range(params.n_runs):
        print(f'run {run + 1} / {params.n_runs}', end = '\r', flush = True)
        
        # Create model
        model = Party_model(prob_stimulus = params.prob_stimulus,
                            prob_interaction = params.prob_interaction,
                            prob_move = params.prob_move,
                            prob_link = params.prob_link,
                            params = params,
                            network = network)

        # Run model
        for iteration in range(params.n_iterations):
            model.step()

        # Save results
        agent_data = safe_run_data(agent_data, model.datacollector.get_agent_vars_dataframe(), run)
        model_data = safe_run_data(model_data, model.datacollector.get_model_vars_dataframe(), run)
        
    
    ## Visualize results
    print('saving results ...', end = '\r', flush = True)

    # Set location
    result_path = make_path(network)

    # Plots network structure
    nx.draw(model.graph, node_size = 10)
    plt.savefig(f"{result_path}network_{model.network}.png")
    plt.clf()

    # Plot the number of voters over time
    sns.lineplot(data = model_data,
                 x = 'Step',
                 y = 'voters',
                 errorbar = 'sd')
    plt.ylim(0, 100)
    plt.savefig(f"{result_path}{model.network}_voters.png")
    plt.clf()

    # Plot the mean political participation over time
    sns.lineplot(data = agent_data,
                 x = 'Step',
                 y = 'political participation',
                 errorbar = 'sd')
    plt.ylim(0,12)
    plt.savefig(f"{result_path}{model.network}_mean_pp.png")
    plt.clf()

    # Plot number of agents with certain level of political participation over time
    for pp in range(13):
        sns.lineplot(data = agent_data[agent_data["political participation"] == pp].groupby(['Step', 'run']).count(),
                     x = 'Step',
                     y = 'political participation',
                     errorbar = 'sd',
                     label = pp)
    plt.ylabel('count')
    plt.legend()
    plt.savefig(f"{result_path}{model.network}_agents_per_pp.png")
    plt.clf()

    # Plot number of agents within certain ranges of political participation over time
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

    # Save numerical results
    pp = (agent_data.groupby(['Step', 'political participation']).count()['AgentID'] / params.n_runs).reset_index()
    pp = pp[pp['Step'] >= params.n_iterations - 100].groupby('political participation').mean().reset_index()[['political participation', 'AgentID']]
    with open(result_path + model.network, 'w') as file:
        file.write(model_data.groupby('Step').mean()['voters'].iloc[-1000:-1].to_string(header=False, index=False) + '\n')

        file.write(f"Apathetic: {pp[pp['political participation'] == 0]['AgentID'].sum()}\n")
        file.write(f"Spectators: {pp[(pp['political participation'] > 0) & (pp['political participation'] <= 4)]['AgentID'].sum()}\n")
        file.write(f"Transitionals: {pp[(pp['political participation'] > 4) & (pp['political participation'] <= 7)]['AgentID'].sum()}\n")
        file.write(f"Gladiators: {pp[pp['political participation'] > 7]['AgentID'].sum()}\n")


    # Set location
    result_path = make_path('networks')

    # Save graph
    attrs = {node : {'cat' : get_category(node.pps), 'pps' : node.pps} for node in model.graph.nodes}
    nx.set_node_attributes(model.graph, attrs)
    nx.write_graphml(model.graph, f'{result_path}{network}.graphml')

    print('Done!                ')
