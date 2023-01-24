import utils

import numpy as np
import random

class Model(object):
    '''
    description: a Model object holds the environment parameters and manages all the agents.
    inputs:
        - prob_stimulus: optional, probability that a stimulus happens to all agents each step
        - prob_interaction = optional, probability that an agent interacts each step,
        - prob_move = optional, probability that an agent moves community,
        - until_eligible = optional, steps needed for new agents to be allowed to vote,
        - characteristics_affected = optional, dictionary of affected characteristics when agent is
          exposed to stimulus
    functions:
        - add_agent(agent): adds an agent to the model
        - step(): updates environment and takes a step for each agent
        - get_pps(): returns data of all agents' political participation over time
    '''

    def __init__(self,
                 prob_stimulus = 0,
                 prob_interaction = 0,
                 prob_move = 0,
                 until_eligible = 0,
                 n_agents = 100,
                 m_barabasi = 5,
                 fermi_alpha = 4,
                 fermi_b = 1,
                 #connections_per_step = 5
                 characteristics_affected = {'active' : .5,
                                             'overt' : .5,
                                             'continuous' : .5,
                                             'expressive' : .5,
                                             'outtaking' : .5}):
        '''
        description: initializes new Model object
        inputs:
            - prob_stimulus: probability that a stimulus happens to all agents each step
            - prob_interaction = probability that an agent interacts each step,
            - prob_move = probability that an agent moves community,
            - until_eligible = steps needed for new agents to be allowed to vote,
            - characteristics_affected = dictionary of effect of stimulus on agent
        '''
        self.prob_stimulus = utils.set_valid(prob_stimulus, upper = 1, verbose = True, name = 'p')
        self.prob_interaction = utils.set_valid(prob_interaction, upper = 1, verbose = True, name = 'q')
        self.prob_move = utils.set_valid(prob_move, upper = 1, verbose = True, name = 'r')
        self.until_eligible = until_eligible
        self.characteristics_affected = characteristics_affected
        self.n_agents = n_agents
        self.m_barabasi = m_barabasi
        self.fermi_alpha = fermi_alpha
        self.fermi_b = fermi_b
        #self.connections_per_step = connections_per_step

        self.time = 0
        self.agents = np.array([])
        self.graph = nx.barabasi_albert_graph(n=self.n_agents, m=self.m_barabasi)


    def add_agent(self, agent):
        '''
        description: adds agent to the model
        input:
            - agent object to add to the model
        '''
        self.agents = np.append(self.agents, agent)


    def step(self):
        '''
        description: updates environment and takes a step for each agent
        '''
        self.time += 1

        # check whether stimulus happens for all agents
        stimulus = random.uniform(0, 1) < self.prob_stimulus

        for agent in self.agents:
            # perform stimulus if applicable
            if stimulus:
                agent.stimulus(self.characteristics_affected.keys())
            # let agent interact according to probability
            if random.uniform(0, 1) < self.prob_interaction:
                agent.interact()
            # move agent according to probability
            if random.uniform(0, 1) < self.prob_move:
                agent.move_community()
            agent.age()
            agent.update_pp()


    # def get_pps(self):
    #     '''
    #     description: returns data of all agents' political participation over time
    #     output:
    #          - ndarray of shape (n_agents, time) of the political participation of each agent at each timestep
    #     '''
    #     return np.array([agent.pps for agent in self.agents])
