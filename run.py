from model import Model
from agents import Agent

import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

n_agents = 100
n_contacts = 0
n_iterations = 250
char_distr = 'normal' # could also be 'uniform'
until_eligible = 4 # from a preset
characteristics_affected = ['active', 'overt', 'continuous', 'expressive', 'outtaking'] # from a preset
p = 0
q = 0
r = 0

# create model
model = Model(p = p, 
              q = q,   
              r = r,
              characteristics_affected = characteristics_affected)

# create agents
if char_distr == 'normal':
    mu = 2
    distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
    samples = distr.rvs(n_agents * 8)
    characteristics = np.reshape(samples, (n_agents, 8))
elif char_distr == 'uniform':
    characteristics = np.random.uniform(0, 4, (n_agents, 8))

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
                          ses = random.uniform(0, 2)))

# create communities
for agent in model.agents:
    for _ in range(n_contacts):
        choice = random.choice(np.delete(model.agents, agent))
        agent.add_contact(choice)

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