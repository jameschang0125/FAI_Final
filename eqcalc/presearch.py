from eqcalc.search import searcher as SS
import numpy as np
from pre.equireader import Equireader as EQ
from random import random
from itertools import product
from eqcalc.state import State

class presearcher():
    def __init__(self, prekeeprate = 0.5, predrawrate = 0.1, debug = True, preactfunc = None, **kwargs):
        self.equitizer = EQ()
        self.ss = SS(**kwargs)
        self.keeprate = prekeeprate # unused
        self.drawrate = predrawrate
        self.debug = debug
        if preactfunc is None:
            self.actfunc = self.act
        else:
            self.actfunc = preactfunc
    
    def calc(self, BBchip, turn, rsize, myh, BB = True):
        '''
        return: action, myr(R/C), oppr(R/C)
        convert preflop ranges to postflop
        '''
        cur = State(BBchip, turn = turn, equitizer = self.equitizer)
        v, a, c = self.ss.FR(rsize, cur)
        myid = self.ss.h2h2i(myh)
        c, cold = self.actall(c), c
        act = c[myid] if BB else int(myid <= self.modifier(a, turn)) # int(myid <= a)

        myhs = []
        for i, x in enumerate(c):
            if x == 1: myhs.append(i)
        oppr = self.r2hs(a)
        myr = self.hs2hs(myhs)

        allset = set(self.r2hs(self.ss.nHands - 1))
        myrset, opprset = set(myr), set(oppr)
        for i in allset:
            if i not in myrset and random() < self.drawrate:
                myr.append(i)
        for i in allset:
            if i not in opprset and random() < self.drawrate:
                oppr.append(i)

        # DEBUG
        if self.debug:
            #if BB:
            tmp = []
            for i in range(self.ss.nHands):
                if c[i] == 2: tmp.append(i)
            print(f"[pre calc] BB shoving {self.ss.is2s(tmp)}")
            #else:
            print(f"[pre calc] SB shoving {self.ss.is2s(range(a + 1))}")

        return act, myr, oppr
    
    def modifier(self, x, turn, rate = 0.8):
        rate = ((20 - turn) + rate * (turn - 10)) / 10 if turn < 10 else 1
        if x >= self.ss.nHands - 10: return x
        return int(x * rate)

    def actall(self, c):
        return [self.actfunc(c[0][i], c[1][i]) for i in range(self.ss.nHands)]

    @classmethod
    def act(self, c, a):
        '''
        given c, a prob suggested, output the action
        '''
        if c + a < 0.4:
            return 0
        if a > 0.6:
            return 2
        return 1

    def r2hs(self, r):
        ans = []
        for i in range(r):
            ans += self.i2h(i)
        return [tuple(t) for t in ans]
    
    def hs2hs(self, hs):
        ans = []
        for i in hs:
            ans += self.i2h(i)
        return [tuple(t) for t in ans]
    
    def i2h(self, i):
        h = self.ss.i2h(i)
        x, y = h % 13 + 2, h // 13 + 2
        if x == y:
            ans = []
            for j in range(4):
                for k in range(j):
                    ans.append(sorted(((i, x), (j, x))))
        if x > y: # xys
            return [sorted(((i, x), (i, y))) for i in range(4)]

        ans = [] # xyo
        for i, j in product(range(4), range(4)):
            if i != j: ans.append(sorted(((i, x), (j, y))))
        return ans



        
        