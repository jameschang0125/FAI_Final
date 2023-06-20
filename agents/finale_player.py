from subagent.heuristics import *
from subagent.smallpreflop import SPreflopper as pre
from subagent.smallpostflop import SPostflopper as post
from agents.deep_player import DeepPlayer
from functools import partial
from random import sample
from agents.dps import Dp4, Dp5, Dp6, Dp7, Dp8, Dp9, Dp10, Dp11, Dp12, Dp13, Dp14, Dp15, Dp16
from time import time
import numpy as np

class FinalePlayer(Dp14):
    def __init__(self, **kwargs):
        super().__init__(printerror = False, **kwargs)
        
        # benchmarking
        self.street2id = {'preflop' : 0, 'flop' : 1, 'turn' : 2, 'river' : 3}
        self.decTime, self.recTime = np.zeros(4), np.zeros(4)

    def receive_street_start_message(self, street, *args):
        st, id = time(), self.street2id[street]
        tmp = self._receive_street_start_message(street, *args)
        timeused = time() - st
        if timeused > self.recTime[id]: self.recTime[id] = timeused
        return tmp

    def declare_action(self, valid_actions, hole_card, round_state):
        st, id = time(), self.street2id[round_state['street']]
        tmp = self._declare_action(valid_actions, hole_card, round_state)
        timeused = time() - st
        if timeused > self.decTime[id]: self.decTime[id] = timeused
        return tmp

def setup_ai(**kwargs):
    return FinalePlayer(**kwargs)
