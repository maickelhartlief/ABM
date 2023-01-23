# these are the tunable parameters to set the political landscape 
# used for presets in the base model
n_agents = 100
n_iterations = 5000
char_distr = 'normal' # could also be 'uniform'
until_eligible = 0
characteristics_affected = {'active' : .9, 
                            'overt' : .9, 
                            'continuous' : .1, 
                            'expressive' : .9, 
                            'outtaking' : .9}
prob_stimulus = 0
prob_interaction = 1
prob_move = 0