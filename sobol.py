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
from SALib.sample import saltelli
from SALib.analyze import sobol
from mesa.batchrunner import BatchRunner
import matplotlib.pyplot as plt
from itertools import combinations
from numpy import isnan


# Prevent mesa's deprecation warnings that can't really be solved since the new version is 
# buggy and has very poor documentation.
filterwarnings("ignore") 

# Import parameter configuration from file based on input argument (default: configs.normal)
params = get_config()
replicates = params.n_runs
max_steps = params.n_iterations
distinct_samples = params.n_distinct_samples
problem = params.problem

# Set the outputs
model_reporters = {"voters" : lambda m : m.get_voters()}
param_values = saltelli.sample(problem, distinct_samples, calc_second_order = False)

# Create batchrunner
batch = BatchRunner(Party_model, 
                    max_steps = max_steps,
                    variable_parameters = {name : [] for name in problem['names']},
                    model_reporters = model_reporters)

# Run for all combinations of parameter values
voters_per_run = []
for run in range(replicates):
    for idx, vals in enumerate(param_values): 
        vals = list(vals) # Change parameters that should be integers
        
        # Transform to dict with parameter names and their values
        variable_parameters = {name : val for name, val in zip(problem['names'], vals)}
        
        # Run model
        batch.run_iteration(variable_parameters, tuple(vals), run)
        print(f'run {run * len(param_values) + idx} / {replicates * len(param_values)}', end = '\r', flush = True)

print('saving results...       ', end = '\r', flush = True)

def plot_index(s, params, i, title=''):
    """
    Description: creates a plot for Sobol sensitivity analysis that shows the contributions
                 of each parameter to the global sensitivity.

    Inputs:
        - s: dictionary of dictionaries that hold
             the values for a set of parameters
        - params: the parameters taken from s
        - i: string that indicates what order the sensitivity is.
        - title: title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~isnan(errors)]
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
    '''
    Description: plots the first and total order sensitivity of parameters
    Inputs:
        - Si: sensitivity
        - problem: dictionary of parameters to perform sensitivity analysis on
    '''

    # set location
    result_path = make_path('sensitivity_analysis')
    
    # First order
    plot_index(Si, problem['names'], '1', 'First order sensitivity')
    plt.savefig(f"{result_path}first-order_sensitivity_{params.networks[0]}.png")
    plt.clf()

    # Total order
    plot_index(Si, problem['names'], 'T', 'Total order sensitivity')
    plt.savefig(f"{result_path}total-order_sensitivity_{params.networks[0]}.png")
    plt.clf()

voters_per_run = batch.get_model_vars_dataframe()['voters'].values
Si_voters = sobol.analyze(problem, voters_per_run, calc_second_order = False)
plot_global(Si_voters, problem)
print('done!            ')
