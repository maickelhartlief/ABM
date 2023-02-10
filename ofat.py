###### ofat.py
# Run local sensitivity analisys (one factor a time) for 'prob_stimulus',  
# 'prob_interaction', 'prob_move', and 'prob_link', using the parameters in 
# normal.py and the first element of networks as the network structure. Also 
# saves plots and results.
####

# Internal imports
from party import Party_model
from utils import make_path, get_config

# External imports
import os
from IPython.display import clear_output
from mesa.batchrunner import BatchRunner
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from agents import Member
from warnings import filterwarnings


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
model_reporters = {"voters": lambda m: m.get_voters()}

data = {}
for idx, var in enumerate(problem['names']):
    print(f'varying {var}')
    
    # Generate uniform samples within the bounds
    samples = np.linspace(*problem['bounds'][idx], num = distinct_samples)
    
    # Run Model for all parameter values
    batch = BatchRunner(Party_model, 
                        max_steps = max_steps,
                        iterations = replicates,
                        variable_parameters = {var : samples},
                        model_reporters = model_reporters)    
    batch.run_all()
    
    # Save results
    data[var] = batch.get_model_vars_dataframe()

# Write results to file
path = make_path('excel')
for var in problem['names']:
    pd.DataFrame.from_dict(data[var]).to_csv(f'{path}{var}.csv')

## visualize results


def plot_param_var_conf(ax, df, var, param, i):
    """
    Description: helper function for plot_all_vars. Plots the individual parameter vs
                 variables passed.

    Inputs:
        - ax: the axis to plot to
        - df: data to be plotted
        - var: variables from df to plot
        - param: which dependent variable to plot
    """
    x = df.groupby(var).mean().reset_index()[var]
    y = df.groupby(var).mean()[param]

    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)

    ax.plot(x, y, c='k')
    ax.fill_between(x, y - err, y + err)

    ax.set_xlabel(var)
    ax.set_ylabel(param)


def plot_all_vars(df, param):
    """
    Description: Plots the parameters passed vs each of the output variables.

    Inputs:
        - df: data to be plotted
        - param: the parameter to be plotted
    """
    f, axs = plt.subplots(4, sharex = False, figsize = (7, 10))
    f.tight_layout()
    
    for idx, var in enumerate(problem['names']):
        plot_param_var_conf(axs[idx], data[var], var, param, idx)


# set location
result_path = make_path()

plot_all_vars(data, 'voters') 
plt.savefig(f"{result_path}OFAT.png")
plt.show()