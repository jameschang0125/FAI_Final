from multiplay import play2

def plays(xs, *args, **kwargs):
    x, y = xs
    return play2(x, y, *args, pe = True, **kwargs)

from tqdm.contrib.concurrent import process_map
import numpy as np
from sklearn.utils import shuffle
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai
from agents.deep_player import setup_ai as deep_ai
from agents.my_player   import setup_ai as aof_ai
from agents.dps         import dps

bosses = [baseline4_ai, baseline5_ai, aof_ai, deep_ai]
ais = [*dps]

def trial(num = 10):
    works, rec, nais = [], [], len(ais)
    for i in range(nais):
        for j in range(i):
            works += [(ais[i], ais[j]) for _ in range(num)]
            rec += [(i, j) for _ in range(num)]
        for j, boss in enumerate(bosses):
            works += [(ais[i], boss) for _ in range(num)]
            rec += [(i, nais + j) for _ in range(num)]
    
    works, rec = shuffle(works, rec)
    r = process_map(plays, works, max_workers = 40, chunksize = 2)
    tsize = (nais, nais + len(bosses))
    wr, err = np.zeros(tsize), np.zeros(tsize)
    for i in range(len(r)):
        x, y = rec[i]
        if r[i] is None:
            err[x][y] += 1
            if y < nais: err[x][y] += 1
        else:
            wr[x][y] += r[i]
            if y < nais: wr[y][x] += 1 - r[i]
    
    for i in range(nais):
        for j in range(nais + len(bosses)):
            if i == j: wr[i][j] = 0.5
            else:
                wr[i][j] /= num - err[i][j]
                err[i][j] /= num
    return np.array(wr), np.array(err)

def crit11(wr, err):
    x = wr * ((1 - err) ** 0.5)
    return x ** 5 + 5 * x ** 4 * (1 - x) + 10 * x ** 3 * (1 - x) ** 2

def crit1(wr, err):
    tmp = np.array([crit11(wr[i], err[i]) for i in range(len(wr))])
    return tmp.prod() ** (1 / len(tmp))

def crit(wr, err):
    return np.array([crit1(wr[i], err[i]) for i in range(len(wr))])

if __name__ == '__main__':
    wr, err = trial(num = 80)
    with np.printoptions(precision = 3, suppress = True):
        print(f"wr:\n{wr}\nerr:\n{err}\ncrit:\n{crit(wr, err)}")
