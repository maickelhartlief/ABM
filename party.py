import utils

import numpy as np
import random
from mesa import Agent, Model, space, time,  DataCollector
import networkx as nx


class Party_model(Model):
    '''
    description: a Party object holds the environment parameters and manages all the agents.
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
                 #outer_agent,
                 prob_stimulus,
                 prob_interaction,
                 prob_move,
                 prob_friend,
                 until_eligible,
                 characteristics_affected,
                 edges_per_step = 1,
                 n_agents = 100,
                 network = 'default', #Can be default, randomn of similarity
                 m_barabasi = 5,
                 fermi_alpha = 4,
                 fermi_b = 1):
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
        self.prob_friend = utils.set_valid(prob_friend, upper = 1, verbose = True, name = "prob_friend")
        self.until_eligible = until_eligible
        self.characteristics_affected = characteristics_affected
        self.edges_per_step = edges_per_step
        self.n_agents = n_agents

        self.network = network
        self.m_barabasi = m_barabasi
        self.fermi_alpha = fermi_alpha
        self.fermi_b = fermi_b

        self.schedule = time.RandomActivation(self)
        self.time = 0
        self.agents = np.array([])
        self.stimulus = False


        self.datacollector = DataCollector(agent_reporters = {"PPS":"pps"})

        if self.network == "default":
            self.graph = nx.complete_graph(n=self.n_agents)
        else:
            self.graph = nx.barabasi_albert_graph(n=self.n_agents, m=self.m_barabasi)


    def add_agent(self, agent):
        '''
        description: adds agent to the model
        input:
            - agent object to add to the model
        '''
        self.agents = np.append(self.agents, agent)
        self.schedule.add(agent)


    def step(self):
        '''
        description: updates environment and takes a step for each agent
        '''
        self.time += 1 # TODO: might already be tracked in scheduler

        # check whether stimulus happens for all agents
        self.stimulus = random.uniform(0, 1) < self.prob_stimulus

        self.datacollector.collect(self)
        self.schedule.step()


    def get_voters(self):
        return len([1 for agent in self.agents if agent.pps >= 2])
