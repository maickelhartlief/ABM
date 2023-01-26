# these are the tunable parameters to set the political landscape
# used for presets in the base model
n_agents = 100
n_iterations = 7000
char_distr = 'normal' # could also be 'uniform'
until_eligible = 0
characteristics_affected = {'active' : .9,
                            'overt' : .9,
                            'continuous' : .1,
                            'expressive' : .9,
                            'outtaking' : .9}
edges_per_step = 5
prob_stimulus = 1
prob_interaction = 1
prob_move = 1 / 2000
prob_friend = 1 / 9
m_barabasi = 5
fermi_alpha = 4
fermi_b = 1.8
