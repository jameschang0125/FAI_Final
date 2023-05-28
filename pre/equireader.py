from eqcalc.search import searcher as SS
from eqcalc.state import State
import pickle
import numpy as np
from pre.equitizer import Equitizer as EQ

class Equireader(EQ):
    def __init__(self, loadpath = "pre/res/eq.pickle"):
        super().__init__()
        if loadpath: 
            with open(loadpath, 'rb') as f:
                self.eq = pickle.load(f)
    
    def showeq(self, turn):
        print(self.eq[turn])
