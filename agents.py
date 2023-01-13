# TODO:
# meaning of global/local community:
#   it seemse like the base model only looks at 1 local community, 
#   which now means that a person moving always takes the exact 
#   same characteristics as the previous owner of that house. 
#   this seems odd.

import utils

import numpy as np
import random

class Agent(object):

    def __init__(self, 
                 name,
                 model,
                 eligible = True,
                 until_eligible = 0,
                 vote_duty = False,
                 active = 0, 
                 overt = 0, 
                 autonomous = 0, 
                 approaching = 0, 
                 continuous = 0, 
                 outtaking = 0, 
                 expressive = 0, 
                 social = 0,
                 ses = 0,
                 pp = 0):
        self.name = name
        self.model = model
        self.eligible = eligible
        self.until_eligible = until_eligible
        self.vote_duty = vote_duty
        self.active = utils.set_valid('active', active)
        self.overt = utils.set_valid('overt', overt)
        self.autonomous = utils.set_valid('autonomous', autonomous)
        self.approaching = utils.set_valid('approaching', approaching)
        self.continuous = utils.set_valid('continuous', continuous)
        self.outtaking = utils.set_valid('outtaking', outtaking)
        self.expressive = utils.set_valid('expressive', expressive)
        self.social = utils.set_valid('social', social)
        self.ses = utils.set_valid('ses', ses, max = 2)
        self.pps = np.array([utils.set_valid('pp', pp, max = 12)])
        
        # initial settings for contacts and time spent in location
        self.move_community()


    def add_contact(self, agent):
        self.contacts = np.append(self.contacts, agent)


    def remove_contact(self, agent):
        self.contacts = np.delete(self.conacts, agent)


    def modify_characteristic(self, characteristic):
        # small modification because characteristics range from 0-4 here instead of 1-5
        return 3 * (characteristic - randint(1, 2)) / (self.autonomous + self.continuous)


    def stimulus(self, affected):
        # no policital participation means no subjection to stimuli
        if pps[-1] == 0:
            return
        
        # only these 5 characteristics can be affected by stimuli
        if 'active' in affected:
            self.active += modify_characteristic(self.active)
        if 'active' in affected:
            self.overt += modify_characteristic(self.overt)
        if 'active' in affected:
            self.continuous += modify_characteristic(self.continuous)
        if 'active' in affected:
            self.expressive += modify_characteristic(self.expressive)
        if 'active' in affected:
            self.outtaking += modify_characteristic(self.outtaking)


    def interaction_modifier(self):
        # set modification to political participation
        mod = random.randint(0, 1) / (self.autonomous + self.continuous)
        
        # modify less when interaction is cynical
        if random.randint(0, 19 * (self.ses + 1)) == 0:
            mod /= 10

        return mod


    def interact(self):
        # check whether personality would lead to interaction
        if self.pps[-1] < 3:
            return
        if self.social + (self.pps[-1] / 3 + 1) + self.active + random.uniform(0, 2.5) <= 10:
            return

        # pick interaction partner
        partner = random.choice(np.delete(self.model.agents, self))

        
        # check whether partner's personality would accept interaction
        if partner.pps[-1] == 0:
            return
        if partner.social + partner.active + partner.approaching + random.uniform(0, 2.5) <= 10:
            return 

        ## interact
        mod = self.interaction_modifier()
        p_mod = partner.interaction_modifier()

        if self.approaching > partner.approaching:
            partner.approaching += p_mod
        else:
            self.approaching += mod

        pps_diff = self.pps[-1] - partner.pps[-1]
        if pps_diff > 0:
            partner.active += p_mod
            self.overt += p_mod # TODO seems like this should be mod instead of p_mod, but this is what the base model does
        elif pps_diff < 0:
            self.active += mod
            partner.overt += mod

        self.contacts += 1
        partner.contacts += 1
            

    def move_community(self):
        self.spent = 0
        self.contacts = 0

 
    def age(self):
        self.until_eligible -= 1
        if self.until_eligible <= 0:
            self.eligible = True
        self.spent += 1


    def update_pp(self):        
        # TODO currently not updated at all, lol
        self.pps = np.append(self.pps, random.randint(0, 12))
