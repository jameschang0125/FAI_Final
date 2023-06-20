import pickle
from subagent.smallpreflop import SPreflopper
from pre.equireader import Equireader as EQ

class OracleFlop(SPreflopper):
    def __init__(self, *args, oraclepath = 'pre/res/brsize.pickle', **kwargs):
        super().__init__(*args, **kwargs)
        with open(oraclepath, 'rb') as f:
            self.brsize = pickle.load(f)
    
    def rrange(self, u, BB = False, **kwargs):
        x, turn = self.cur.my - EQ.offset, self.cur.turn
        if (turn, x) in self.brsize:
            a, b = self.brsize[(turn, x)]
            if BB: return [] if b is None else [b]
            else: return [] if a is None else [a]
        return []



