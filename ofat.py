###### ofat.py
# 
####

# internal imports
from party import Party_model

# external imports
import os
from IPython.display import clear_output
from mesa.batchrunner import BatchRunner
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from agents import Member

# We define our variables and bounds
problem = {
    'num_vars': 4,
    'names': ['prob_stimulus', 'prob_interaction', 'prob_move', 'prob_link'],
    'bounds': [[0, 0.25], [0, 0.25], [0, 0.1], [0.25, 0.75]]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 10
max_steps = 5000
distinct_samples = 10

# Set the outputs
model_reporters = {"voters": lambda m: m.get_voters()}

data = {}

for i, var in enumerate(problem['names']):
    # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
    samples = np.linspace(*problem['bounds'][i], num = distinct_samples)
    print(samples)
    
    batch = BatchRunner(Party_model, 
                        max_steps = max_steps,
                        iterations = replicates,
                        variable_parameters = {var: samples},
                        model_reporters = model_reporters)
    
    batch.run_all()
    
    data[var] = batch.get_model_vars_dataframe()

# Print and save data in excell
print(data)
df_stimulus = pd.DataFrame.from_dict(data['prob_stimulus'])
df_interaction = pd.DataFrame.from_dict(data['prob_interaction'])
df_move = pd.DataFrame.from_dict(data['prob_move'])
df_link = pd.DataFrame.from_dict(data['prob_link'])
df_stimulus.to_csv('results/excel/data_stimulus.csv')
df_interaction.to_csv('results/excel/data_interaction.csv')
df_move.to_csv('results/excel/data_move.csv')
df_link.to_csv('results/excel/data_link.csv')

def plot_param_var_conf(ax, df, var, param, i):
    """
    Helper function for plot_all_vars. Plots the individual parameter vs
    variables passed.

    Args:
        ax: the axis to plot to
        df: dataframe that holds the data to be plotted
        var: variables to be taken from the dataframe
        param: which output variable to plot
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
    Plots the parameters passed vs each of the output variables.

    Args:
        df: dataframe that holds all data
        param: the parameter to be plotted
    """

    f, axs = plt.subplots(4, sharex=False, figsize=(7, 10))
    f.tight_layout()
    
    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], data[var], var, param, i)

## visualize results
# set location
result_path = 'results'
if not os.path.exists(result_path):
   os.makedirs(result_path)
result_path += '/'

plot_all_vars(data, 'voters') 
plt.savefig(f"{result_path}OFAT.png")
plt.show()