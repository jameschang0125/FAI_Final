import pickle
from src.pre.winrater import winRater as WR
from tqdm import tqdm
from itertools import product
from functools import partialmethod
import numpy as np

class RangeProcesser():
    nHands = 13 * 13

    def __init__(self, boot = True,
                frepath = "src/pre/res/ifr.pickle",
                h2ipath = "src/pre/res/h2i.pickle", 
                i2hpath = "src/pre/res/i2h.pickle", 
                wrtpath = "src/pre/res/idwr.pickle", **kwargs):
        
        if boot:
            with open(frepath, 'rb') as f:
                self.fq = pickle.load(f)
            with open(h2ipath, 'rb') as f:
                self.h2i = pickle.load(f)
            with open(i2hpath, 'rb') as f:
                self.i2h = pickle.load(f)
            with open(wrtpath, 'rb') as f:
                self.wr = pickle.load(f)
            
            self.fw = self.wr * self.fq
            self.fwSum = self._2dsum(self.fw)
            self.wrSum = self._2dsum(self.wr)
            self.fqSum = self._2dsum(self.fq)

    def _2dsum(self, x):
        n, m = x.shape
        ans = np.copy(x)
        for i in range(n):
            for j in range(m):
                if i >= 1: ans[i][j] += ans[i - 1][j] 
                if j >= 1: ans[i][j] += ans[i][j - 1]
                if i >= 1 and j >= 1: ans[i][j] -= ans[i - 1][j - 1]
        return ans

    def _sumrect(self, x, i = None, j = None):
        '''
        boundary: BOTH INCLUDED
        '''
        if i is None: i = (0, x.shape[0] - 1)
        if j is None: j = (0, x.shape[1] - 1)
        i1, i2 = i
        j1, j2 = j
        i1, j1 = i1 - 1, j1 - 1
        ans = x[i2][j2]
        if i1 >= 0: ans -= x[i1][j2]
        if j1 >= 0: ans -= x[i2][j1]
        if i1 >= 0 and j1 >= 0: ans += x[i1][j1]

        return ans

    def rvr(self, i, j):
        return self.__rvr((0, i), (0, j))

    def rvr2(self, i, j, k):
        return self.__rvr((0, i), (j, k))

    def r2vr(self, i, j, k):
        return self.__rvr((i, j), (0, k))

    def r2vr2(self, i, j, k, w):
        return self.__rvr((i, j), (k, w))

    def rvh(self, i, j):
        return self.__rvr((0, i), (j, j))

    def hvr(self, i, j):
        return self.__rvr((i, i), (0, j))

    def hvr2(self, i, j, k):
        return self.__rvr((i, i), (j, k))

    def hvh(self, i, j):
        return self.wr[i][j]
    
    def hsvh(self, i, j):
        fw, tf = 0, 0
        for k in range(self.nHands):
            if i[k]:
                fw += self.fw[k][j]
                tf += self.fq[k][j]
        return fw / tf
    
    def hvrEq(self, i, j):
        '''
        Note: this can be modified
        '''
        return self.hvr(i, j)

    def rprob(self, i, BB = True):
        return self._sumrect(self.fqSum, (0, i)) if BB else self._sumrect(self.fqSum, j = (0, i))
    
    def r2prob(self, i, j, BB = True):
        return self._sumrect(self.fqSum, (i, j)) if BB else self._sumrect(self.fqSum, j = (i, j))

    def prob(self, i, BB = True):
        return self._sumrect(self.fqSum, (i, i)) if BB else self._sumrect(self.fqSum, j = (i, i))

    def combprob(self, i, j):
        return self.fq[i][j]


    def rprob_h(self, i, h, BB = True):
        '''
        compute rprob GIVEN my hand = h
        '''
        if BB:
            tmp = self.prob(h, BB = False)
            if tmp == 0: return (i + 1) / self.nHands(BB = False)
            return self._sumrect(self.fqSum, (0, i), (h, h)) / tmp
        tmp = self.prob(h)
        if tmp == 0: return (i + 1) / self.nHands(BB = True)
        return self._sumrect(self.fqSum, (h, h), (0, i)) / tmp

    def rprob_r(self, i, r, BB = True):
        '''
        compute rprob GIVEN my range = r
        Notice the direction
        '''
        if BB:
            tmp = self.rprob(r, BB = False)
            # print(f"rprob_r : {self._sumrect(self.fqSum, (0, i), (0, r))}/{tmp}")
            if tmp == 0: return (i + 1) / self.nHands(BB = False)
            return self._sumrect(self.fqSum, (0, i), (0, r)) / tmp
        tmp = self.rprob(r)
        if tmp == 0: return (i + 1) / self.nHands(BB = True)
        return self._sumrect(self.fqSum, (0, r), (0, i)) / tmp

    def r2prob_r(self, i, j, r, BB = True):
        if BB:
            tmp = self.rprob(r, BB = False)
            if tmp == 0: return (j - i + 1) / self.nHands(BB = False)
            return self._sumrect(self.fqSum, (i, j), (0, r)) / tmp
        tmp = self.rprob(r)
        if tmp == 0: return (j - i + 1) / self.nHands(BB = True)
        return self._sumrect(self.fqSum, (0, r), (i, j)) / tmp

    def __rvr(self, i, j):
        '''
        i, j: tuple
        '''
        tmp = self._sumrect(self.fqSum, i, j)
        if tmp == 0: return 0.5
        return self._sumrect(self.fwSum, i, j) / tmp
    

