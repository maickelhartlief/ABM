###### utils.py
# Contains some extra static functions used in the program
####

# External imports
from math import sqrt
from importlib import import_module
import pandas as pd
import os
import sys


def set_valid(param, lower = 0, upper = 5, verbose = False, name = ''):
    '''
    description: returns closest value of param that is within bounds
    inputs:
        - param: desired parameter value
        - lower: optional, lower limit for the parameter
        - upper: optional, upper limit for the parameter
        - verbose: optional, whether to print if the desired value is invalid
        - name: optional, name of the parameter, for printing (only relevant if verbose)
    outputs:
        - closest valid parameter value
    '''
    valid = True
    out = param

    if param < lower:
        valid = False
        out = lower
    elif param > upper:
        valid = False
        out = upper

    if verbose and not valid:
        print(f'invalid value for {name}: {param}. set to {out}')

    return out


def distance_normalizer(distance):
    '''
    description: normalizes a distance to be inbetween .5 and 2, so that the max 
                 and min modification is doubling or halfing.
    inputs:
        - distance: number to be normalized to [.5 - 2]
    outputs:
        - [.5 - 2] normalized distance
    '''
    return distance / sqrt(5**2 * 3 + 2**2) * 1.5 + .5


def safe_run_data(data, run_data, run):
    '''
    description: formats and adds the data of 1 run to the full dataframe of results.
    inputs:
        - data: the full dataframe of results
        - run_data: unformatted results of current run of the model
        - run: which number run run_data came from
    outputs:
        - data with run_data formatted and added to it
    '''
    run_data = run_data.reset_index().rename(columns = {'index' : 'Step'})
    run_data['run'] = run
    return pd.concat([data, run_data], ignore_index = True)


def make_path(path = ''):
    '''
    description: creates folder(s) to save results into
    inputs:
        path: (nested) folder(s) to create in results/
    outputs:
        path of the results (results/[path]/)
    '''
    result_path = 'results' + ('' if path == '' else '/') + path
    if not os.path.exists(result_path):
       os.makedirs(result_path)
    return result_path + '/'


def get_config(config = None):
    '''
    description: retrieves hyperparameters from config file (uses configs/normal.py if none given)
    outputs:
        - hyperparameters form config file
    '''
    return import_module('configs.' + (config if config is not None else ('normal' if len(sys.argv) < 2 else sys.argv[1])))

# Categorize agents to save as graph
def get_category(pp):
    '''
    description: return category of agetn based on political participation.
    inputs:
        - pp: political participation score [0-12]
    outputs:
        - category (0 = apathetic, 1 = spectator, 2 = transitional, 3 = gladiator)
    '''
    if pp == 0:
        return 0
    if 1 <= pp <= 4:
        return 1
    if 5 <= pp <=7:
        return 2

    return 3