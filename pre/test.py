from pre.realtime_processer import RealtimeProcesser as RP
from eqcalc.research import researcher as RS
from itertools import product
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from eqcalc.search import searcher as SS # hs2s

import numpy as np

def testeq():
    eqold = EQ(eqpath = "pre/res/eq.pickle")
    eq = EQ()
    np.set_printoptions(precision = 3, suppress = True)
    for i in range(1, 21):
        print(f"--- {i} ---")
        # print(eqold.eq[i])
        print(eq.eq[i])
    

def testrp(comm = [(2, 13), (2, 14), (2, 5)]):
    pos = [(i, j) for i, j in product(range(4), range(2, 15))]
    BBr = []
    for i in range(len(pos)):
        for j in range(i):
            BBr.append((pos[i], pos[j]))
    SBr = BBr
    r = RP(BBr, SBr, comm)
    return r

def rpr(rp, i, r):
    tmp = rp.rprob(r, BB = False)
    if tmp == 0: return (i + 1) / rp.nHands(BB = False)
    tmp2 = rp._sumrect(rp.fqSum, (0, i), (0, r))
    print(f"rpr({i}, {r}) = {tmp2}/{tmp} = {tmp2 / tmp}")
    return tmp2 / tmp

def testrs():
    rp = testrp()
    rs = RS(rp)
    eq = EQ()
    cur = State(1000, turn = 19, equitizer = eq)
    ret = rs.CR(20, 80, cur)

    BBr = [rp.i2h(i) for i in range(rp.nHands(BB = True))]
    BBr = [rp.h2s(h) for h in BBr]
    print(BBr)

    '''
    for i in [10, 20, 30]:
        print(f"i :: {rp.rvh(0, i)}")

    print(rp.r2vr(0, rp.nHands(BB = True) - 1, rp.nHands(BB = False) - 1))
    print(rp.r2vr(1, rp.nHands(BB = True) - 1, rp.nHands(BB = False) - 1))
    print(rp.r2vr(2, rp.nHands(BB = True) - 1, rp.nHands(BB = False) - 1))
    '''
    #print(rp.fq[0])
    #print(rp.fq[1])
    #rpr(rp, 10, 0)

    # rp.rprob_r(10, 0, BB = True)
    # print(ret)

def testpostAoF():
    rp = testrp(comm = [(2, 3), (3, 7), (4, 4)])
    rs = RS(rp)
    eq = EQ()
    cur = State(990, turn = 19, equitizer = eq)

    m, n = rp.nHands(BB = True), rp.nHands(BB = False)
    BBr, SBr = rp.is2s(range(m)), rp.is2s(range(n), BB = False)

    for it, decay in ((3001, 0.98), (51, 0.8), (51, 0.83), (51, 0.86), (51, 0.89), (51, 0.92), (51, 0.94), (51, 0.96)):
        print(f"\n{(it, decay)} :: ")

        myr, myrc, oppr, opprc, opprc2 = rs.R_AoF(20, 250, cur, it, decay = decay)

        #for i in range(m):
        #    print(f"{BBr[i]}: CA = {'%.3f'%myr[i]}, RA = {'%.3f'%myrc[i]}")
        
        #print(f"\n------------------------------------\n")

        for i in range(10):
            print(f"{SBr[i]}: R = {'%.3f'%oppr[i]}, RAA = {'%.3f'%opprc[i]}, CAA = {'%.3f'%opprc2[i]}")



