from eqcalc.state import State
from eqcalc.search import searcher as SS
import numpy as np
from pre.hand_processer import HandProcesser as HP
from pre.equitizer import Equitizer as EQ

def testrs():
    ss = SS()
    '''
    h = HP.genHand(6, 4)
    id = ss.h2h2i(h)
    print(id, ss.i2s(id))
    '''
    eq = EQ()
    print(eq.wr(18, 875))
    print(eq._iswin(18, 875))

    for bet in [300]: # [15, 20, 25, 40, 80, 200]:
        print(f"\n------- bet = {bet} -------")
        cur = State(860, equitizer = eq)
        ret = ss.FR(bet, cur)
        print(ret)


