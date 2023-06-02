from pre.realtime_processer import RealtimeProcesser as RP
from eqcalc.research import researcher as RS
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from random import random

class postsearcher():
    '''
    addresses the problem that researcher is not very consistent (due to random sampling)
    '''
    def __init__(self, keeprate = 0.5, drawrate = 0.2):
        self.equitizer = EQ()
        self.keeprate = keeprate
        self.drawrate = drawrate

    def calc(self, BBchip, turn, pot, rsize, myr, myh, oppr, comm, nSearch = 3):
        '''
        return: a(C) == A, a(R) == A, myr(C/C), oppr(C/C)
        '''
        myh = sorted(myh)
        pos = [(i, j) for i, j in product(range(4), range(2, 15))]
        myr, oppr = self.purify(myr, comm), self.purify(oppr, comm)

        cur = State(BBchip, turn = turn, equitizer = self.equitizer)
        
        CA, RA, MYR, OPPR = 0, 0, [], []
        for _ in range(nSearch):
            ca, ra, myr2, oppr2 = self.__calc(myr, oppr, comm, cur, myh)
            CA += int(ca)
            RA += int(ra)
            MYR += myr2
            OPPR += oppr2

        CA /= nSearch
        RA /= nSearch

        myrset, opprset = set(MYR), set(OPPR)
        for i in myr:
            if i not in myrset and random() < self.drawrate:
                MYR.append(i)
        for i in oppr:
            if i not in opprset and random() < self.drawrate:
                OPPR.append(i)
        
        return CA, RA, MYR, OPPR
    
    @classmethod
    def __calc(self, myr, oppr, comm, cur, myh):
        rp = RP(myr, oppr, comm, myh)
        rs = RS(rp)
        myid = rs.h2i(myh)
        v, c, Rc, Cc, Ccc = rs.CR(pot, rsize, cur)

        # a(C) == A
        CA, RA = myid <= Cc, myid <= Rc

        myr2 = myr[(Cc + 1):] if Cc + 1 < rp.nHands(BB = True) else []
        for i in range(Cc + 1):
            if random() < self.keeprate:
                myr2.append(rs.i2h(i))

        oppr2 = oppr[(c + 1):] if c + 1 < rp.nHands(BB = True) else []
        for i in range(c + 1):
            if random() < self.keeprate:
                oppr2.append(rs.i2h(i))

        return CA, RA, oppr2

    @classmethod
    def purify(self, x, y):
        x, y = set(x), set(y)
        ans = []
        for a, b in x:
            if a in y or b in y: continue
            ans.append([a, b])
        return ans

