from pre.realtime_processer import RealtimeProcesser as RP
from eqcalc.research import researcher as RS
from itertools import product
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from eqcalc.search import searcher as SS # hs2s

def testrp():
    pos = [(i, j) for i, j in product(range(4), range(2, 15))]
    BBr = []
    for i in range(len(pos)):
        for j in range(i):
            BBr.append((pos[i], pos[j]))
    SBr = BBr
    comm = [(2, 13), (2, 14), (2, 5)]
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

