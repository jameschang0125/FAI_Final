import numpy as np
import pickle
from src.pre.winrater import winRater as WR
from tqdm import tqdm
from itertools import product
from functools import partialmethod

from src.eqcalc.search import searcher as SS # SS.h2s

class RangePreProcesser():
    nHands = 13 * 13

    def __init__(self):
        self.WR = WR()

    def gen(self, 
            frepath = "src/pre/res/ifr.pickle",
            h2ipath = "src/pre/res/h2i.pickle", 
            i2hpath = "src/pre/res/i2h.pickle", 
            wrtpath = "src/pre/res/idwr.pickle", **kwargs):
        '''
        generates: 
            id <-> hand
            wr(id) table
        '''
        self.buildFreqTable()
        wr = self.avgrwr(**kwargs)
        id2hand = np.flip(np.argsort(wr))
        hand2id = np.zeros(self.nHands, dtype = 'int16')
        hand2id[id2hand] = np.arange(self.nHands)

        wrtable = np.zeros((self.nHands, self.nHands))
        freqs = np.zeros((self.nHands, self.nHands))
        for i in range(self.nHands):
            for j in range(self.nHands):
                wrtable[i][j] = self.WR.wr(id2hand[i], id2hand[j])
                freqs[i][j] = self.freq[id2hand[i]][id2hand[j]]
        freqs = freqs / np.sum(freqs)

        with open(frepath, 'wb') as f:
            pickle.dump(freqs, f)
        with open(h2ipath, 'wb') as f:
            pickle.dump(hand2id, f)
        with open(i2hpath, 'wb') as f:
            pickle.dump(id2hand, f)
        with open(wrtpath, 'wb') as f:
            pickle.dump(wrtable, f)

        # DEBUG
        print(id2hand)
        print(wrtable[0].tolist())
        print([SS.h2s(h) for h in id2hand])

    def avgrwr(self, cutoffs = [0.1, 0.2, 0.37, 0.6, 1], **kwargs):
        ans = np.zeros(self.nHands)
        for c in cutoffs:
            ans += self.robustwr(cutoff = c, **kwargs)
        return ans / len(cutoffs)

    def robustwr(self, iter = 1000, cutoff = 0.3, **kwargs):
        oppr = np.arange(self.nHands)
        wr = self.calcwr(oppr)
        N = int((1 - cutoff) * self.nHands)

        for i in tqdm(range(1, iter)):
            oppr = np.argsort(wr)[N:]
            wr2 = self.calcwr(oppr)
            wr = (wr * i + wr2) / (i + 1)
        return wr

    def calcwr(self, oppr):
        '''
        O(NN)
        '''
        return np.array([self.wr(i, oppr) for i in range(self.nHands)])

    def wr(self, x, oppr):
        '''
        O(N)
        '''
        tf, tw = 0, 0
        for i in oppr:
            tf += self.freq[x][i]
            tw += self.freq[x][i] * self.WR.wr(x, i)
        return tw / tf

    def buildFreqTable(self):
        ans = np.zeros((13 * 13, 13 * 13))
        for xi, xj, yi, yj in product(range(13), range(13), range(13), range(13)):
            ans[xi + xj * 13][yi + yj * 13] = self._freq(xi, xj, yi, yj)
        self.freq = ans
        return ans
                
    def _freq(self, xi, xj, yi, yj):
        x, y = self._en(xi, xj), self._en(yi, yj)
        l = len(set((x[0], x[1], y[0], y[1])))

        if x[2] == 2 and y[2] == 2:
            return 6 if x[0] == y[0] else 6 * 6
        elif x[2] == 2:
            if y[2] == 0:
                return 6 * 2 * 3 if l == 2 else 6 * 4 * 3
            else:
                return 6 * 2 if l == 2 else 6 * 4
        elif y[2] == 2:
            if x[2] == 0:
                return 6 * 2 * 3 if l == 2 else 6 * 4 * 3
            else:
                return 6 * 2 if l == 2 else 6 * 4
        elif l == 4:
            return 4 * 4 * (3 ** (2 - x[2] - y[2]))
        elif l == 3:
            return 4 * 3 * (3 ** (2 - x[2] - y[2]))
        else: # l == 2
            if x[2] + y[2] == 2: return 4 * 3
            if x[2] + y[2] == 1: return 4 * 3 * 2
            if x[2] + y[2] == 0: return 4 * 3 * 4 * 3 - 4 * 3 - 4 * 3 * 2

    def _en(self, x, y):
        '''
        ENCODING: o, s, p = 0, 1, 2
        '''
        m, n = max(x, y), min(x, y)
        if x > y:
            return (m, n, 0)
        if x < y:
            return (m, n, 1)
        if x == y:
            return (m, n, 2)