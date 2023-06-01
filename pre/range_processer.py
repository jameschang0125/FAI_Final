import pickle
from pre.winrater import winRater as WR
from tqdm import tqdm
from itertools import product
from functools import partialmethod
import numpy as np

class RangeProcesser():
    nHands = 13 * 13

    def __init__(self, boot = True,
                frepath = "pre/res/ifr.pickle",
                h2ipath = "pre/res/h2i.pickle", 
                i2hpath = "pre/res/i2h.pickle", 
                wrtpath = "pre/res/idwr.pickle", **kwargs):
        
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

    def _sumrect(self, x, i, j = (0, nHands - 1)):
        '''
        boundary: BOTH INCLUDED
        '''
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

    def rvh(self, i, j):
        return self.__rvr((0, i), (j, j))

    def hvr(self, i, j):
        return self.__rvr((i, i), (0, j))

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

    def rprob(self, i):
        return self._sumrect(self.fqSum, (0, i))

    def prob(self, i):
        return self._sumrect(self.fqSum, (i, i))

    def rprob_h(self, i, h):
        '''
        compute rprob GIVEN my hand = h
        '''
        return self._sumrect(self.fqSum, (h, h), (0, i)) / self.prob(h)

    def rprob_r(self, i, r):
        '''
        compute rprob GIVEN my range = r
        '''
        return self._sumrect(self.fqSum, (0, r), (0, i)) / self.rprob(r)

    def __rvr(self, i, j):
        '''
        i, j: tuple
        '''
        return self._sumrect(self.fwSum, i, j) / self._sumrect(self.fqSum, i, j)
    

