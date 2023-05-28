from eqcalc.state import State
from eqcalc.search import searcher as SS
import numpy as np
from pre.hand_processer import HandProcesser as HP
from pre.equireader import Equireader as EQ

def testrs():
    ss = SS()
    '''
    h = HP.genHand(6, 4)
    id = ss.h2h2i(h)
    print(id, ss.i2s(id))
    '''
    eq = EQ()
    tests = [(0, 1000), (1, 1005), (1, 1000), (1, 995), (1, 990)]
    for t in tests:
        print(f"{t}: {eq._iswin(*t)}, {eq.wr(*t)}")
    # print(eq.eq.shape, eq.eq[1]) # should be 0.5

    
    for bet in [400]: # [15, 20, 25, 40, 80, 200]:
        print(f"\n------- bet = {bet} -------")
        cur = State(990, turn = 0, equitizer = eq)
        ret = ss.FR(bet, cur, verbose = True)
        print(ret)
    


