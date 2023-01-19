import utils

import numpy as np
import random
from mesa import Agent, Model, space, time

class Party_agent(Agent):
    def __init__(self,
                 unique_id,
                 model,
                 prob_stimulus = 0,
                 prob_interaction = 0,
                 prob_move = 0,
                 until_eligible = 0,
                 characteristics_affected = {'active' : .5, 
                                             'overt' : .5, 
                                             'continuous' : .5, 
                                             'expressive' : .5, 
                                             'outtaking' : .5}):
        self.unique_id = unique_id
        self.model = model
        self.inner_model = Party_model(self,
                                       prob_stimulus,
                                       prob_interaction,
                                       prob_move,
                                       until_eligible,
                                       characteristics_affected)
        self.fitness = self.advance()


    def step(self):
        self.inner_model.step()


    def advance(self):
        ## TODO: figure out what the fitness should be
        # total political participation
        self.fitness = np.sum(self.inner_model.get_pps())
        # total number of voters
        # self.fitness = self.inner_model.get_voters()


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
                 until_eligible,
                 characteristics_affected):
        '''
        description: initializes new Model object
        inputs:
            - prob_stimulus: probability that a stimulus happens to all agents each step
            - prob_interaction = probability that an agent interacts each step,
            - prob_move = probability that an agent moves community,
            - until_eligible = steps needed for new agents to be allowed to vote,
            - characteristics_affected = dictionary of effect of stimulus on agent
        '''
        #self.outer_agent = outer_agent
        self.prob_stimulus = utils.set_valid(prob_stimulus, upper = 1, verbose = True, name = 'p')
        self.prob_interaction = utils.set_valid(prob_interaction, upper = 1, verbose = True, name = 'q')
        self.prob_move = utils.set_valid(prob_move, upper = 1, verbose = True, name = 'r')
        self.until_eligible = until_eligible
        self.characteristics_affected = characteristics_affected

        self.schedule = time.RandomActivation(self)
        self.time = 0
        self.agents = np.array([])
        self.stimulus = False


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
        
        self.schedule.step()


    def get_pps(self):
        '''
        description: returns data of all agents' political participation over time
        output:
             - ndarray of shape (n_agents, time) of the political participation of each agent at each timestep
        '''
        return np.array([agent.pps for agent in self.agents])


    def get_voters(self):
        return len([1 for agent in self.agents if agent.pps >= 2])


