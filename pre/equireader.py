from eqcalc.search import searcher as SS
from eqcalc.state import State
import pickle
import numpy as np
from pre.equitizer import Equitizer as EQ

class Equireader(EQ):
    def __init__(self, 
                eqpath = "pre/res/AoFeq.pickle", 
                BBrpath = "pre/res/AoFBBr.pickle", 
                SBrpath = "pre/res/AoFSBr.pickle"):

        super().__init__()
        if eqpath: 
            with open(eqpath, 'rb') as f:
                self.eq = pickle.load(f)
        if BBrpath: 
            with open(BBrpath, 'rb') as f:
                self.BBr = pickle.load(f)
        if SBrpath: 
            with open(SBrpath, 'rb') as f:
                self.SBr = pickle.load(f)
    
    def showeq(self, turn):
        print(self.eq[turn])
