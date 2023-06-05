from pre.realtime_processer import RealtimeProcesser as RP
from eqcalc.research import researcher as RS
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from random import random
import numpy as np

class postsearcher():
    '''
    addresses the problem that researcher is not very consistent (due to random sampling)
    '''
    def __init__(self, postkeeprate = 0.5, postdrawrate = 0.2, debug = True, 
                postactfunc = None, postnSearch = 5, **kwargs):
        self.equitizer = EQ()
        self.keeprate = postkeeprate
        self.drawrate = postdrawrate
        self.debug = debug
        
        self.actfunc = self.act if postactfunc is None else postactfunc

        self.nSearch = postnSearch
        self.kwargs = kwargs

    def calc(self, BBchip, turn, pot, rsize, myr, myh, oppr, comm):
        '''
        return: a(C) == A, a(R) == A, myr(C/C), oppr(C/C)
        '''
        #myh = tuplesorted(myh)
        myr, oppr = self.purify(myr, comm), self.purify(oppr, comm)

        cur = State(BBchip, turn = turn, equitizer = self.equitizer)
        
        CA, RA, MYR, OPPR = 0, 0, [], []
        for _ in range(self.nSearch):
            ca, ra, myr2, oppr2 = self.__calc(myr, oppr, comm, cur, myh, pot, rsize)
            CA += int(ca)
            RA += int(ra)
            MYR += myr2
            OPPR += oppr2

        CA /= self.nSearch
        RA /= self.nSearch

        myrset, opprset = set(MYR), set(OPPR)
        for i in myr:
            if i not in myrset and random() < self.drawrate:
                MYR.append(i)
        for i in oppr:
            if i not in opprset and random() < self.drawrate:
                OPPR.append(i)

        if self.debug:
            print(f"[POST] C - A = {CA}, R - A = {RA}")

        return self.actfunc(CA), self.actfunc(RA), MYR, OPPR
    
    def __calc(self, myr, oppr, comm, cur, myh, pot, rsize):
        rp = RP(myr, oppr, comm, myh)
        rs = RS(rp, **self.kwargs)
        myid = rp.h2i(myh)

        # CA, RA, R, RAA, CAA
        myr, myrc, oppr, opprc, opprc2 = rs.R_AoF(pot, rsize, cur)

        ca, ra = myr[myid], myrc[myid]

        myr2, oppr2, m, n = [], [], rp.nHands(BB = True), rp.nHands(BB = False)
        for i in range(m):
            if random() < myr[i] + self.keeprate:
                myr2.append(rp.i2h(i, BB = True))
        for i in range(n):
            if random() < oppr[i] + self.keeprate:
                oppr2.append(rp.i2h(i, BB = False))

        '''
        v, c, Rc, Cc, Ccc = rs.CR(pot, rsize, cur)

        # a(C) == A
        CA, RA = myid <= Cc, myid <= Rc

        myr2 = myr[(Cc + 1):] if Cc + 1 < rp.nHands(BB = True) else []
        for i in range(Cc + 1):
            if random() < self.keeprate:
                myr2.append(rp.i2h(i))

        oppr2 = oppr[(c + 1):] if c + 1 < rp.nHands(BB = True) else []
        for i in range(c + 1):
            if random() < self.keeprate:
                oppr2.append(rp.i2h(i))
        '''

        # DEBUG
        if self.debug:
            print(f"[__calc] C-A : {rp.hs2s(rp.is2h(np.where(myr > 0.9)[0]))}")
            print(f"[__calc] R-A : {rp.hs2s(rp.is2h(np.where(myrc > 0.9)[0]))}")

        return ca, ra, myr2, oppr2

    @classmethod
    def act(self, act):
        return 1 if act > 0.9 else (0 if act < 0.1 else int(random() < act ** 2))

    @classmethod
    def purify(self, x, y):
        x, y = set(x), set(y)
        ans = []
        for a, b in x:
            if a in y or b in y: continue
            ans.append((a, b))
        return ans

