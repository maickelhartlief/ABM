from political_participation import PPmodel
import SALib
from SALib.sample import saltelli
import pandas as pd
from mesa.batchrunner import BatchRunner
from IPython.display import clear_output
from SALib.analyze import sobol
import matplotlib.pyplot as plt
from itertools import combinations
import numpy as np

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 10
max_steps = 5000
distinct_samples = 10

# We define our variables and bounds
problem = {
    'num_vars': 4,
    'names': ['prob_stimulus', 'prob_interaction', 'prob_move', 'prob_link'],
    'bounds': [[0, 0.25], [0, 0.25], [0, 0.1], [0.25, 0.75]]
}

# Set the outputs
model_reporters = {"voters": lambda m: m.schedule.get_voters()}

# We get all our samples here
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=False)

# READ NOTE BELOW CODE
batch = BatchRunner(PPmodel, 
                    max_steps=max_steps,
                    variable_parameters={name:[] for name in problem['names']},
                    model_reporters=model_reporters)

count = 0
data = pd.DataFrame(index=range(replicates*len(param_values)), 
                                columns=['prob_stimulus', 'prob_interaction', 'prob_move', 'prob_link'])
data['Run'], data['voters'] = None, None

for i in range(replicates):
    for vals in param_values: 
        # Change parameters that should be integers
        vals = list(vals)
        # Transform to dict with parameter names and their values
        variable_parameters = {}
        for name, val in zip(problem['names'], vals):
            variable_parameters[name] = val

        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]
        iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
        data.iloc[count, 0:4] = vals
        data.iloc[count, 4:8] = iteration_data
        count += 1

        clear_output()
        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')

print(data)

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
    # First order
    plot_index(Si, problem['names'], '1', 'First order sensitivity')
    plt.savefig("results/sobol/First-order-sensitivity.png")
    plt.clf()

    # Total order
    plot_index(Si, problem['names'], 'T', 'Total order sensitivity')
    plt.savefig("results/sobol/Total-order-sensitivity.png")
    plt.clf()

Si_voters = sobol.analyze(problem, data['voters'].values, calc_second_order=False)
plot_global(Si_voters, problem)