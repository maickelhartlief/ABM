# these are the tunable parameters to set the political landscape 
# used for presets in the base model
n_agents = 100
n_iterations = 5000
char_distr = 'normal' # could also be 'uniform'
until_eligible = 4
characteristics_affected = {'active' : .4, 
                            'overt' : .5, 
                            'continuous' : .5, 
                            'expressive' : .5, 
                            'outtaking' : .5}
prob_stimulus = 1 / 8
prob_interaction = 1 / 2
prob_move = 1 / 260