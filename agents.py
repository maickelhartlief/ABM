# TODO:
# meaning of global/local community:
#   it seemse like the base model only looks at 1 local community, 
#   which now means that a person moving always takes the exact 
#   same characteristics as the previous owner of that house. 
#   this seems odd.

from utils import set_valid

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
                 char_modifiers = {'active' : .5, 
                                   'overt' : .5, 
                                   'continuous' : .5, 
                                   'expressive' : .5, 
                                   'outtaking' : .5}):
        self.name = name
        self.model = model
        self.eligible = eligible
        self.until_eligible = until_eligible
        self.vote_duty = vote_duty
        self.active = set_valid(active, verbose = True, name = 'active')
        self.overt = set_valid(overt, verbose = True, name = 'overt')
        self.autonomous = set_valid(autonomous, verbose = True, name = 'autonomous')
        self.approaching = set_valid(approaching, verbose = True, name = 'approaching')
        self.continuous = set_valid(continuous, verbose = True, name = 'continuous')
        self.outtaking = set_valid(outtaking, verbose = True, name = 'outtaking')
        self.expressive = set_valid(expressive, verbose = True, name = 'expressive')
        self.social = set_valid(social, verbose = True, name = 'social')
        self.ses = set_valid(ses, lower = 1, upper = 3, verbose = True, name = 'ses')
        self.pps = np.array([])
        self.char_modifiers = char_modifiers
        
        # initial settings for contacts and time spent in location
        self.move_community()
        
        # initialize ppz
        self.update_pp()
        
        


    def modify_characteristic(self, characteristic):
        # small modification because characteristics range from 0-4 here instead of 1-5
        return 3 * (self.char_modifiers[characteristic] - random.randint(0, 1)) / (self.autonomous + self.continuous)


    def stimulus(self, affected):
        # no policital participation means no subjection to stimuli
        if self.pps[-1] == 0:
            return
        
        # only these 5 characteristics can be affected by stimuli
        # NOTE: the netlogo code only checks whether values are valid after this step, 
        #       meaning that over or underflow in autonomous and continuous will change 
        #       the output of modify_charactastics(). we check it immediately.
        if 'active' in affected:
            self.active = set_valid(self.modify_characteristic('active') + self.active)
        if 'overt' in affected:
            self.overt = set_valid(self.modify_characteristic('overt') + self.overt)
        if 'continuous' in affected:
            self.continuous = set_valid(self.modify_characteristic('continuous') + self.continuous)
        if 'expressive' in affected:
            self.expressive = set_valid(self.modify_characteristic('expressive') + self.continuous)
        if 'outtaking' in affected:
            self.outtaking = set_valid(self.modify_characteristic('outtaking') + self.continuous)


    def interaction_modifier(self):
        # set modification to political participation
        mod = random.randint(0, 1) / (self.autonomous + self.continuous)
        
        # modify less when interaction is cynical
        if random.randint(0, int(19 * self.ses)) == 0:
            mod /= 10

        return mod


    def interact(self):
        # check whether personality would lead to interaction
        if self.pps[-1] < 3:
            return
        if self.social + (self.pps[-1] / 3 + 1) + self.active + random.uniform(0, 2.5) <= 10:
            return

        # pick interaction partner
        partner = random.choice(self.model.agents)
        while partner == self:
            partner = random.choice(self.model.agents)

        
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
        self.time_in_community = 1
        self.contacts = 0

 
    def age(self):
        self.until_eligible -= 1
        if self.until_eligible <= 0:
            self.eligible = True
        self.time_in_community += 1


    def update_pp(self):
        self.pps = np.append(self.pps, 0 if random.uniform(0, 1) > .1 else 1)
        
        if not self.eligible:
            return
        
        # NOTE base model says there should maybe be stochasticity here, but there isn't yet
        # NOTE: probably a mistake in base model where vote duty alone does not envoke checks for higher levels.
        if self.vote_duty or self.active + self.approaching - (5 / 3) * self.ses > 3:
            self.pps[-1] = 2
        else:
            return

        # NOTE: base model uses model time, instead of time spent in community of agent. the latter makes much more sense
        if self.active + self.overt + self.approaching + self.social + (2.5 * self.contacts ) / self.time_in_community  > 15:
            self.pps[-1] = 3
        else:
            return
        
        if self.overt + self.expressive > 6:
            self.pps[-1] = 4
        else:
            return

        if self.overt + self.autonomous + self.approaching + self.outtaking > 12:
            self.pps[-1] = 5
        else:
            return

        if self.active + self.approaching - self.outtaking + self.expressive - self.social > 3:
            self.pps[-1] = 6
        else:
            return

        if self.overt + self.social + (2.5 * self.contacts ) / self.time_in_community > 9:
            self.pps[-1] = 7
        else:
            return

        if self.active + self.overt + self.approaching + self.outtaking + self.expressive + (5 / 3) * self.ses > 18:
            self.pps[-1] = 8
        else:
            return

        if self.continuous + self.expressive + (5 / 3) * self.ses > 9:
            self.pps[-1] = 9
        else:
            return

        if self.active + self.overt + self.continuous + (5 / 3) * self.ses > 12:
            self.pps[-1] = 10
        else:
            return

        if self.active + self.overt + self.approaching + self.continuous + (2.5 * self.contacts) / self.time_in_community + (5 / 3) * self.ses > 18:
            self.pps[-1] = 11
        else:
            return

        if self.active + self.overt + self.autonomous + self.approaching + self.continuous - self.outtaking + (2.5 * self.contacts) / self.time_in_community + (5 / 3) * self.ses > 18:
            self.pps[-1] = 12
        else:
            return

