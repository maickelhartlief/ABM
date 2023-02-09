Requirements:
- math
- sys
- os
- random
- matplotlib
- numpy
- scipy
- lib
- mesa
- networkx
- seaborn
- panda
- SALib
- IPython
- itertools
- scikit_posthocs

files:
- run.py: 
- ofat.py: 
- sobol.py: 
- statistics.py: 

- party.py: 
- agents.py: 
- utils.py: 

- normal.py: 

parameters:
- `n_runs (int)`: Number of independent runs to run each network type for
- `n_agents (int)`: Number of agents in the model
- `n_iterations (int)`: Number of steps to run the model for
- char_distr (str): Distribution used to initialize the characteristics of the agents
- until_eligible (int): Steps until newly moved agents are allowed to vote
- characteristics_affected (dict{str['active', 'overt', 'continuous', 'expressive', 'outtaking'] : float[0-1]}): Whether characteristics are affected by events (pressence in the dictionary) and how they are affected (<.5 tends down, >.5 tends up)
- edges_per_step (int): TODO
- prob_stimulus (float[0-1]): Probability that a stimulus happens to all agents at any step
- prob_interaction (float[0-1]): Probability that any agent tries to find another agent to interact with at any step
- prob_move (float[0-1]): Probability that any agent gets reset (simulates moving community and getting replaced by another agent)
- prob_link (float[0-1]): TODO
- m_barabasi (float): TODO
- fermi_alpha (float): TODO
- fermi_b (float): TODO
- networks (list{str['not_connected', 'holme_kim', 'homophily', 'fully_connected']}): Which type of network structure(s) to run the model with. 'not_connected' has no links, 'holme_kim' has a common social network structure, 'homophily' has a social network structure based on similarities in the agents' characteristics, and 'fully_connected'