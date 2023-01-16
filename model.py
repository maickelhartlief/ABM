import utils

import numpy as np
import random

class Model(object):

    def __init__(self,
                 prob_stimulus = 0,
                 prob_interaction = 0,
                 prob_move = 0,
                 characteristics_affected = []):
        self.prob_stimulus = utils.set_valid(prob_stimulus, upper = 1, verbose = True, name = 'p')
        self.prob_interaction = utils.set_valid(prob_interaction, upper = 1, verbose = True, name = 'q')
        self.prob_move = utils.set_valid(prob_move, upper = 1, verbose = True, name = 'r')
        self.characteristics_affected = characteristics_affected

        self.time = 0
        self.agents = np.array([])


    def add_agent(self, agent):
        self.agents = np.append(self.agents, agent)


    def removed_agent(self, agent):
        self.agents = np.delete(self.agents, agent)


    def step(self):
        self.time += 1
        stimulus = random.uniform(0, 1) < self.prob_stimulus
        for agent in self.agents:
            if stimulus:
                agent.stimulus(self.characteristics_affected)
            if random.uniform(0, 1) < self.prob_interaction:
                agent.interact()
            if random.uniform(0, 1) < self.prob_move:
                agent.move_community()
            agent.age()
            agent.update_pp()


    def get_pps(self):
        return np.array([agent.pps for agent in self.agents])


