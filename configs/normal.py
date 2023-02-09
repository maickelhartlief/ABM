###### normal.py
# A configuration file with hyperparameters. Alternatives can easily be made by copying 
# this code to another file in the same folder and calling run.py with the name of that 
# file as an input variable
####

n_runs = 3
n_agents = 100
n_iterations = 1000
char_distr = 'normal'
until_eligible = 4
characteristics_affected = {'active' : .4,
                            'overt' : .5,
                            'continuous' : .5,
                            'expressive' : .59,
                            'outtaking' : .5}
edges_per_step = 10
prob_stimulus = 1 / 8
prob_interaction = 1 / 8
prob_move = 1 / 260
prob_link = 1/2
m_barabasi = 2
fermi_alpha = 4
fermi_b = 1.8
networks = ['homophily']
