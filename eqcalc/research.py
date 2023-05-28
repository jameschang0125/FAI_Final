from pre.range_processer import RangeProcesser as RP
from eqcalc.state import State
import numpy as np

class researcher():
    '''
    This is a POSTFLOP calculator.
    Suppose we have the range of BB and SB is given. 
    However, we allow them to have a chance to contain hands out-of-range.
    
    Notice that the range representation in preflop and postflop is not the same.
    
    Similar to PREFLOP, we suppose the possible lines are:
    (BB R -- SB F/C/A)
    (BB C -- SB C/R -- BB F/C/A)
    
    We suppose that raise range is LINEAR. This affects the performance but accelerate a lot.
    '''

    nHands = 26 * 51

    def CR(self, myr, oppr, state, pot, bet):
        


        





