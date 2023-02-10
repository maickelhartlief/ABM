###### homophily.py
# A configuration file with hyperparameters for running only the homophily network.
####

# Use parameters in normal.py as default
from configs.normal import *

# The paramters to overwrite
n_runs = 3
networks = ['homophily']