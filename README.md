This code was made by *Maickel Hartlief*, *Arend Geerlofs*, *Dominique Weltevreden*, *Kaat Brinksma*, and *Mirjam Koedijk*

**Requirements**:
- `math`
- `sys`
- `os`
- `random`
- `matplotlib`
- `numpy`
- `scipy`
- `lib`
- `mesa`
- `networkx`
- `seaborn`
- `panda`
- `SALib`
- `IPython`
- `itertools` 
- `scikit_posthocs`
- `warnings`

**How to use**:

To run the model, run `run.py`. 

Hyperparameters can be changed by changing them in `normal.py` in the `configs` folder, or by copying `normal.py` into `[name].py` and calling `run.py` with input argument `[name]`.

To do sensitivity analisys, run `ofat.py` (local) or `sobol.py` (global). These use the first element in the `network` parameter in the `normal.py` config file, so make sure to change that to the network you want to run the sensitivity analisys on.

To do statistical analysis on the results of the model, run `statistics.py`. This uses the results saved when running `run.py`, so make sure to do that beforehand.

**Files**:
- `run.py`: Runs the model with the hyperparameters set in `normal.py`, unless another file is specified as input argument, and saves plots and graphs into the `results` folder.
- `ofat.py`: Run local sensitivity analisys (one factor a time) for `'prob_stimulus'`, ` 'prob_interaction'`, `'prob_move'`, and `'prob_link'`, using the parameters in `normal.py` and the first element of networks as the network structure. Also saves plots and results.
- `sobol.py`: Runs global sensitivity analisys for `'prob_stimulus'`, ` 'prob_interaction'`, `'prob_move'`, and `'prob_link'`, using the parameters in `normal.py` and the first element of networks as the network structure. Also saves plots and results.
- `statistics.py`: TODO
- `party.py`: Specifies the `Party_model` class which is a subclass of a `mesa.Model`. This represents the environment of the model and handles all global functionality like environment variables, data collection, initializing agents, and calling the agents' step functions each step.
- `agents.py`: Speficies the `Member` class which is a subclass of a `mesa.Agent`. This represents the agents of the model and handles characteristics, interacting, and has the dependent variable political participation.
- `utils.py`: Some useful functions that are used elsewhere in the program.
- `normal.py`: A configuration file with hyperparameters. Alternatives can easily be made by copying this code to another file in the `config` folder and calling `run.py` with the name of that file as an input variable.

**parameters**:
- `n_runs (int)`: Number of independent runs to run each network type for.
- `n_agents (int)`: Number of agents in the model.
- `n_iterations (int)`: Number of steps to run the model for.
- `n_distinct_samples`: how many sample values to take for each parameter during sensitivity analysis.
- `char_distr (str)`: Distribution used to initialize the characteristics of the agents.
- `until_eligible (int)`: Steps until newly moved agents are allowed to vote.
- `characteristics_affected (dict{str['active', 'overt', 'continuous', 'expressive', 'outtaking'] : float[0-1]})`: Whether characteristics are affected by events (pressence in the dictionary) and how they are affected (<.5 tends down, >.5 tends up).
- `edges_per_step (int)`: TODO
- `prob_stimulus (float[0-1])`: Probability that a stimulus happens to all agents at any step.
- `prob_interaction (float[0-1])`: Probability that any agent tries to find another agent to interact with at any step.
- `prob_move (float[0-1])`: Probability that any agent gets reset (simulates moving community and getting replaced by another agent).
- `prob_link (float[0-1])`: TODO
- `m_barabasi (float)`: TODO
- `fermi_alpha (float)`: TODO
- `fermi_b (float)`: TODO
- `networks (list{str['not_connected', 'holme_kim', 'homophily', 'fully_connected']})`: Which type of network structure(s) to run the model with. `'not_connected'` has no links, `'holme_kim'` has a common social network structure, `'homophily'` has a social network structure based on similarities in the agents' characteristics, and `'fully_connected'` has a link between every 2 agents.

