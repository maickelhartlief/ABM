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

data = pd.DataFrame()
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
    var_data = batch.get_model_vars_dataframe().rename(columns = {var : 'val'})
    var_data['var'] = var
    data = pd.concat([data, var_data])

# Write results to file
path = make_path('sensitivity_analysis')
data.to_csv(f'{path}ofat.csv')


## visualize results

# Set location
result_path = make_path('sensitivity_analysis')

# Plot voters per value for changing parameters
fig, axs = plt.subplots(4, sharex = False, figsize = (7, 10))
fig.tight_layout()

# Subplot per variable tested for sensitivity
for idx, var in enumerate(problem['names']):
    var_data = data[data['var'] == var].drop(columns = ['Run']).groupby('val').agg(['mean', 'std']).reset_index()
    var_data['err'] = (1.96 * var_data['voters']['std']) / np.sqrt(replicates)
    
    axs[idx].plot(var_data['val'].values, var_data['voters']['mean'].values, c = 'k')
    axs[idx].fill_between(var_data['val'].values, var_data['voters']['mean'] - var_data['err'], var_data['voters']['mean'] + var_data['err'])

    axs[idx].set_xlabel(var)
    axs[idx].set_ylabel('voters')

plt.savefig(f"{result_path}ofat.png")