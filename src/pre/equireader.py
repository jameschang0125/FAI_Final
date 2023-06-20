from src.eqcalc.search import searcher as SS
from src.eqcalc.state import State
import pickle
import numpy as np
from src.pre.equitizer import Equitizer as EQ

class Equireader(EQ):
    def __init__(self, 
                eqpath = "src/pre/res/Deepeq.pickle", # "pre/res/AoFeq.pickle", 
                BBrpath = "src/pre/res/AoFBBr.pickle", 
                SBrpath = "src/pre/res/AoFSBr.pickle"):

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
        with np.printoptions(precision = 4, suppress = True):
            print(self.eq[turn])
