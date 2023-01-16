from model import Model
from agents import Agent

import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

n_agents = 50
n_iterations = 10000
char_distr = 'normal' # could also be 'uniform'
until_eligible = 4 # from a preset
characteristics_affected = ['active', 'overt', 'continuous', 'expressive', 'outtaking'] # from a preset
prob_stimulus = .25
prob_interaction = .75
prob_move = 0

# create model
model = Model(prob_stimulus = prob_stimulus, 
              prob_interaction = prob_interaction,   
              prob_move = prob_move,
              characteristics_affected = characteristics_affected)

# create agents
if char_distr == 'normal':
    mu = 2
    distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
    samples = distr.rvs(n_agents * 8)
    characteristics = np.reshape(samples, (n_agents, 8))
elif char_distr == 'uniform':
    characteristics = np.random.uniform(0, 5, (n_agents, 8))

for idx in range(n_agents):
    model.add_agent(Agent(idx, 
                          model,
                          eligible = random.uniform(0, 1) < .8,
                          until_eligible = until_eligible,
                          vote_duty = random.uniform(0, 1) < .03,
                          active = characteristics[idx, 0], 
                          overt = characteristics[idx, 1], 
                          autonomous = characteristics[idx, 2], 
                          approaching = characteristics[idx, 3], 
                          continuous = characteristics[idx, 4], 
                          outtaking = characteristics[idx, 5], 
                          expressive = characteristics[idx, 6], 
                          social = characteristics[idx, 7],
                          ses = random.uniform(1, 3)))

# run simulation
for iteration in range(n_iterations):
    model.step()

# visualize results
pps = model.get_pps()
plt.plot(np.mean(pps, axis = 0))
plt.show()

for pp in range(13):
    plt.plot(np.count_nonzero(pps == pp, axis = 0), label = pp)
plt.legend()
plt.show()


plt.plot(np.count_nonzero(pps == 0, axis = 0), label = '0')
plt.plot(np.count_nonzero((pps > 0) & (pps <= 4), axis = 0), label = '1-4')
plt.plot(np.count_nonzero((pps > 5) & (pps <= 7), axis = 0), label = '5-8')
plt.plot(np.count_nonzero(pps >= 8, axis = 0), label = '8-12')
plt.legend()
plt.show()