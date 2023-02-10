###### sobol.py
# Runs global sensitivity analisys for 'prob_stimulus', 'prob_interaction', 
# 'prob_move', and 'prob_link', using the parameters in normal.py and the first
# element of networks as the network structure. Also saves plots and results.
####

# Internal imports
from party import Party_model
from utils import make_path, get_config

# External imports
from warnings import filterwarnings
import SALib
from SALib.sample import saltelli
import pandas as pd
from mesa.batchrunner import BatchRunner
from IPython.display import clear_output
from SALib.analyze import sobol
import matplotlib.pyplot as plt
from itertools import combinations
from importlib import import_module
import numpy as np
import sys


# prevent mesa's deprecation warnings that can't really be solved since the new version is 
# buggy and has very poor documentation.
filterwarnings("ignore") 

# Import parameter configuration from file based on input argument 
# (default: configs.normal)
params = get_config()

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = params.n_runs
max_steps = params.n_iterations
distinct_samples = params.n_distinct_samples

# We define our variables and bounds
problem = {
    'num_vars': 4,
    'names': ['prob_stimulus', 'prob_interaction', 'prob_move', 'prob_link'],
    'bounds': [[0, 0.25], [0, 0.25], [0, 0.1], [0.25, 0.75]]
}

# Set the outputs
model_reporters = {"voters" : lambda m : m.get_voters()}

# Get all samples
param_values = saltelli.sample(problem, distinct_samples, calc_second_order = False)

# READ NOTE BELOW CODE
batch = BatchRunner(Party_model, 
                    max_steps = max_steps,
                    variable_parameters = {name : [] for name in problem['names']},
                    model_reporters = model_reporters)

count = 0
data = pd.DataFrame(index = range(replicates * len(param_values)), 
                    columns = ['prob_stimulus', 'prob_interaction', 'prob_move', 'prob_link'])
data['Run'], data['voters'] = np.nan, np.nan

for _ in range(replicates):
    for vals in param_values: 
        # Change parameters that should be integers
        vals = list(vals)
        # Transform to dict with parameter names and their values
        variable_parameters = {name : val for name, val in zip(problem['names'], vals)}
        
        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]
        iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
        data.iloc[count, 0:4] = vals
        data.iloc[count, 4:8] = iteration_data
        count += 1

        clear_output()
        print(f'running... ({count / (len(param_values) * (replicates)) * 100:.2f}%)', end = '\r', flush = True)
print('saving results...       ', end = '\r', flush = True)

def plot_index(s, params, i, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

def plot_global(Si, problem):
    # set location
    result_path = make_path('sobol')
    
    # First order
    plot_index(Si, problem['names'], '1', 'First order sensitivity')
    plt.savefig("results/sobol/First-order-sensitivity.png")
    plt.clf()

    # Total order
    plot_index(Si, problem['names'], 'T', 'Total order sensitivity')
    plt.savefig("results/sobol/Total-order-sensitivity.png")
    plt.clf()

Si_voters = sobol.analyze(problem, data['voters'].values, calc_second_order = False)
plot_global(Si_voters, problem)
print('done!            ')