from model import Model
from agents import Agent

import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from importlib import import_module


# import input parameter configuration (default: configs.normal)
params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))

# create model
model = Model(prob_stimulus = params.prob_stimulus, 
              prob_interaction = params.prob_interaction,   
              prob_move = params.prob_move,
              characteristics_affected = params.characteristics_affected)

# create agents
if params.char_distr == 'normal':
    mu = 2
    distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
    samples = distr.rvs(params.n_agents * 8)
    characteristics = np.reshape(samples, (params.n_agents, 8))
elif char_distr == 'uniform':
    characteristics = np.random.uniform(0, 5, (params.n_agents, 8))

for idx in range(params.n_agents):
    model.add_agent(Agent(idx, 
                          model,
                          eligible = random.uniform(0, 1) < .8,
                          until_eligible = params.until_eligible,
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
for iteration in range(params.n_iterations):
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