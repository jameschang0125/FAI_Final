from eqcalc.state import State
from eqcalc.search import searcher as SS
import numpy as np
from pre.hand_processer import HandProcesser as HP

def testrs():
    ss = SS()
    '''
    h = HP.genHand(6, 4)
    id = ss.h2h2i(h)
    print(id, ss.i2s(id))
    '''

    for bet in [409]: # [15, 20, 25, 40, 80, 120]:
        print(f"\n------- bet = {bet} -------")
        cur = State(990)
        ret = ss.FR(bet, cur)
        print(ret)


