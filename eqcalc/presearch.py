from eqcalc.search import searcher as SS
import numpy as np
from pre.equireader import Equireader as EQ
from random import random
from itertools import product

class presearcher():
    def __init__(self, keeprate = 0.5, drawrate = 0.2):
        self.equitizer = EQ()
        self.ss = SS()
        self.keeprate = keeprate
        self.drawrate = drawrate
    
    def calc(self, BBchip, turn, rsize, myh):
        '''
        return: action, myr(R/C), oppr(R/C)
        convert preflop ranges to postflop
        '''
        cur = State(BBchip, turn = turn, equitizer = self.equitizer)
        v, a, c = self.ss.FR(rsize, cur)
        myid = self.ss.h2h2i(myh)
        act = c[myid]

        myhs = []
        for i, x in enumerate(c):
            if x == 1: myhs.append(i)
        oppr = self.r2hs(a)
        myr = self.hs2hs(myhs)

        return act, myr, oppr
    
    def r2hs(self, r):
        ans = []
        for i in range(r):
            ans += self.i2h(i)
        return ans
    
    def hs2hs(self, hs):
        ans = []
        for i in hs:
            ans += self.i2h(i)
        return ans
    
    def i2h(self, i):
        h = self.ss.i2h(i)
        x, y = h % 13 + 2, h // 13 + 2
        if x == y:
            return [sorted([(i, x), (j, x)]) for i in range(j) for j in range(4)]
        if x > y: # xys
            return [sorted([(i, x), (i, y)]) for i in range(4)]

        ans = [] # xyo
        for i, j in product(range(4), range(4)):
            if i != j: ans.append(sorted([(i, x), (j, y)]))
        return ans



        
        