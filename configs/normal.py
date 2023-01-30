# these are the tunable parameters to set the political landscape
# used for presets in the base model
n_agents = 100
n_iterations = 5000
char_distr = 'normal' # could also be 'uniform'
until_eligible = 4
characteristics_affected = {'active' : .4,
                            'overt' : .5,
                            'continuous' : .5,
                            'expressive' : .59,
                            'outtaking' : .5}
edges_per_step = 20
prob_stimulus = 1 / 8
prob_interaction = 1 / 8
prob_move = 1 / 260
# probability that a and c are linked in holme kim; delete later if possible
prob_link = 1/2
m_barabasi = 2
fermi_alpha = 4
fermi_b = 1.8
network = 'holme_kim' #"holme_kim""homophily"'fully_connected''not_connected'
