from src.eqcalc.state import State
from src.eqcalc.search import searcher as SS
import numpy as np
from src.pre.hand_processer import HandProcesser as HP
from src.pre.equireader import Equireader as EQ
from src.util.hand_evaluator import HandEvaluator as HE
from src.util.card import Card
from itertools import product
from tqdm import tqdm

from eqcalc.presearch import presearcher as pre

def testpreR_AoF():
    np.set_printoptions(precision = 3, suppress = True)
    ss = SS()
    eq = EQ()
    cur = State(990, 19, equitizer = eq)
    myr, myrc, oppr, opprc = ss.R_AoF(30, cur)

    print("R - A", myr, "R - C", myrc, sep = "\n")
    print("R", oppr, "R - A - A", opprc, sep = "\n")


def testAoF():
    ss = SS()
    eq = EQ()
    for i, j in [(850, 19), (857, 18), (865, 17)]:
        print(f"\n({i}, {j})")
        cur = State(i, turn = j, equitizer = eq)
        ret = ss.AoF(cur)
        v, a, c = ret
        print(c)
        print(v)


def testpre():
    pres = pre()
    # calc(self, BBchip, turn, rsize, myh, BB = True)
    myh = ((1, 14), (2, 14))
    for stack in [900, 950, 1000, 1050, 1100]:
        print(f"\nstack = {stack}")
        pres.calc(stack, 19, 1000, myh)

def testrs():
    ss = SS()
    '''
    h = HP.genHand(6, 4)
    id = ss.h2h2i(h)
    print(id, ss.i2s(id))
    '''
    eq = EQ()
    tests = [(0, 1000), (1, 1005), (1, 1000), (1, 995), (1, 990)]
    #for t in tests:
    #    print(f"{t}: {eq._iswin(*t)}, {eq.wr(*t)}")
    # print(eq.eq.shape, eq.eq[1]) # should be 0.5

    '''
    for bet in [200]: # [15, 20, 25, 40, 80, 200]:
        print(f"\n------- bet = {bet} -------")
        cur = State(1000, turn = 15, equitizer = eq)
        ret = ss.FR(bet, cur, verbose = True)
        print(ret)
    '''

    '''
    for BBchip in [900, 930, 960, 1000, 1030, 1060, 1100]:
        print(f"\n------- BBchip = {BBchip} -------")
        cur = State(BBchip, turn = 15, equitizer = eq)
        ret = ss.FR(200, cur, verbose = True)
        print(ret)
    '''

    for turn in [19, 15, 12, 10, 8, 5]:
        print(f"\n------- turn = {turn} -------")
        cur = State(950, turn = turn, equitizer = eq)
        ret = ss.FR(200, cur, verbose = True)
        print(ret)


def gen_eval(comm, hands):
    tmp, nHands = [], len(hands)
    for i, h in enumerate(hands):
        tmp.append(HE.eval_hand(h, comm))
    
    ans = np.zeros((nHands, nHands))
    for i in range(nHands):
        for j in range(nHands):
            ans[i][j] = 1 if tmp[i] > tmp[j] else (0.5 if tmp[i] == tmp[j] else 0)
    return ans
    

def testwr():
    hands, possibles = [], [Card(a, b) for a, b in product(range(4), range(2, 15))]
    for i in range(52):
        for j in range(i):
            hands.append([possibles[i], possibles[j]])
    nHands = len(hands)
    comm = ["D6", "D8", "D9", "CA"]
    comm = [Card.from_str(c) for c in comm]

    ans = np.zeros((nHands, nHands))
    for p in tqdm(possibles):
        # ans += gen_eval(comm + [p], hands)
        gen_eval(comm + [p], hands)
    ans /= len(possibles)
    print(ans)


def testarr():
    nHands = 52 * 51 // 2
    ans = np.zeros((nHands, nHands))
    val = [257 * i % 321 for i in range(nHands)]
    for i in tqdm(range(50)):
        ans += np.array([[val[j] > val[k] for k in range(nHands)] for j in range(nHands)])
        val = [(j + 2) % 322 for j in val]

