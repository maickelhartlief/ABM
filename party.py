import utils

import numpy as np
import random
from mesa import Agent, Model, space, time
from mesa.datacollection import DataCollector
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
                 prob_stimulus,
                 prob_interaction,
                 prob_move,
                 prob_link,
                 until_eligible,
                 characteristics_affected,
                 network = 'homophily',
                 edges_per_step = 1,
                 n_agents = 100,
                 m_barabasi = 5,
                 fermi_alpha = 4,
                 fermi_b = 1,
                 dynamic = False,
                 graph=nx.Graph()):
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
        self.prob_link = utils.set_valid(prob_link, upper = 1, verbose = True, name = 'linkage')
        self.until_eligible = until_eligible
        self.characteristics_affected = characteristics_affected
        self.edges_per_step = edges_per_step
        self.n_agents = n_agents
        self.network = network
        self.graph = nx.Graph()
        self.fermi_alpha = fermi_alpha
        self.fermi_b = fermi_b
        self.dynamic = dynamic
        self.network = network


        self.schedule = time.RandomActivation(self)
        self.time = 0
        self.agents = np.array([])
        self.stimulus = False

        self.datacollector = DataCollector(model_reporters = {"voters" : lambda m : self.get_voters()},
                                           agent_reporters = {"political participation" : "pps"})

        # create network
        if network == 'fully_connected':
            self.graph = nx.complete_graph(n = n_agents)
        elif network == "holme_kim":
            self.graph = nx.powerlaw_cluster_graph(n = n_agents, m = m_barabasi, p = prob_link)
        elif network == 'homophily':
            self.graph = nx.Graph()
        elif network == "not_connected":
            self.graph = nx.Graph()

    def add_agent(self, agent):
        '''
        description: adds agent to the model
        input:
            - agent object to add to the model
        '''
        self.agents = np.append(self.agents, agent)
        self.schedule.add(agent)

        # Attaches agent to node
        if (self.network == "homophily") or (self.network == "not_connected"):
            self.graph.add_node(agent)
        else:
            self.graph = nx.relabel_nodes(self.graph, {agent.unique_id: agent})


    def step(self):
        '''
        description: updates environment and takes a step for each agent
        '''
        # check whether stimulus happens for all agents
        self.stimulus = random.uniform(0, 1) < self.prob_stimulus

        # TODO might be worth collecting after the step?

        self.schedule.step()
        self.datacollector.collect(self)


    def get_voters(self):
        return len([True for agent in self.agents if agent.pps >= 2])
