from src.subagent.smallpreflop import SPreflopper as preflopper
from src.pre.deepequitizer import DeepEquitizer as DE
from src.eqcalc.state import State
from itertools import product
from tqdm.contrib.concurrent import process_map
import pickle
import numpy as np
from src.pre.equireader import Equireader as EQ

with open('src/pre/res/gto.pickle', 'rb') as f:
    gto = pickle.load(f)

def epoch11(BBchip, turn, rsize):
    myh = ((0, 14), (1, 14))
    pre = preflopper()
    pre.act(BBchip, turn, myh, rsize)
    return pre.gt.update()

def epoch12(BBchip, turn, rsize1, rsize2):
    myh = ((0, 14), (1, 14))
    pre = preflopper()
    cur = State(BBchip, turn = turn, equitizer = pre.eq)
    pre.nxt, pre.cur = cur.to(), cur
    pre.gt = pre.LimpRaiseTree(cur, rsize1, rsize2)
    pre.act(BBchip, turn, myh)
    return pre.gt.update()

def epoch1(w):
    BBchip, turn = w[1] + DE.offset, w[0]
    x, y = BBchip - DE.offset, DE._iswin(turn, BBchip)
    if y is not None: return None, None

    cur = State(BBchip, turn = turn, equitizer = EQ())
    bestr1, bestv1, bestr2, bestv2 = None, 2, None, -1
    for rsize1 in gto[turn][x]:
        if rsize1 < 15 or rsize1 > cur.thre(False):
            continue
        v = epoch11(BBchip, turn, rsize1)
        if v < bestv1: bestr1, bestv1 = rsize1, v
    # if bestr1 is None: return None, None

    if 10 in gto[turn][x]:
        rrange = gto[turn][x][10]
    else:
        rrange = [int(10 + 2 * 10 * c) for c in [2.2, 1.75, 1.44, 1.2, 1, 0.85, 0.75, 0.67, 0.5, 0.33, 0.25]]

    for rsize2 in rrange:
        if rsize2 < 15 or rsize2 > cur.thre(True):
            continue
        v = epoch12(BBchip, turn, rsize1, rsize2)
        if v > bestv2: bestr2, bestv2 = rsize2, v
    return (bestr1, bestr2)

def run():
    work = [(i, j) for i, j in product(range(1, 21), range(DE.size * 2 + 1))]
    ret = process_map(epoch1, work, max_workers = 40, chunksize = 1)

    ans = {work[i]: ret[i] for i in range(len(work))}
    with open('pre/res/brsize.pickle', 'wb') as f:
        pickle.dump(ans, f)

    print(ans)
