# from pre.winrater import winRater as WR
from pre.range_processer import RangeProcesser as RP
from eqcalc.state import State
import numpy as np

class searcher():
    '''
    This is a PREFLOP calculator. 
    We suppose that SB always F/R and BB always F/C/ALLIN 
    '''

    BB = 10 # SB
    nHands = 13 * 13

    def __init__(self, pen = 0.9):
        self.RP = RP()
        self.pen = pen

    @classmethod
    def h2s(self, h):
        x, y = h % 13, h // 13
        if x < y:
            x, y = y, x
            s = 's'
        elif x == y:
            s = ''
        else:
            s = 'o'
        return "23456789TJQKA"[x] + "23456789TJQKA"[y] + s

    def i2s(self, i):
        '''
        id to string
        '''
        return self.h2s(self.i2h(i))
    
    def r2s(self, r):
        sols = np.where(r == 2)[0]
        return [self.i2s(id) for id in sols]

    def i2h(self, i):
        return self.RP.i2h[i]

    def h2i(self, h):
        return self.RP.h2i[h]
    
    def h2h(self, h):
        x, y = h
        m, n = x.rank - 2, y.rank - 2
        m, n = max(m, n), min(m, n)
        if x.suit == y.suit: m, n = n, m
        return m + n * 13
    
    def h2h2i(self, h):
        return self.h2i(self.h2h(h))

    def FR(self, bet, state):
        '''
        bet : bet size for SB
        '''

        # PRE
        fEV = state.wr(self.BB * 1.5)
        # (f"fEV = {fEV}")

        vac = []
        for i in range(0, self.nHands, 10):
            pr = self.RP.rprob(i)
            vh, ch, cch = self.FCA(bet + self.BB, bet - self.BB, state, i)
            vh = pr * vh + (1 - pr) * fEV
            vac.append((vh, i, ch))
            '''
            # DEBUG
            print(f"raising with range {i}: (p = {pr})")
            print(f"equity = {vh}, BB action: ") 
            print(ch, cch)
            '''
        vac.sort()
        iSet = [vac[j][1] for j in range(3)]
        
        v, a, c, cc = 2, None, None, None
        for j in iSet:
            for i in range(max(0, j - 5), min(self.nHands, j + 5)):
                pr = self.RP.rprob(i)
                vh, ch, cch = self.FCA(bet + self.BB, bet - self.BB, state, i)
                vh = pr * vh + (1 - pr) * fEV

                if vh < v:
                    v, a, c, cc = vh, i, ch, cch

        # DEBUG
        # print(cc)
        return v, a, c

    def FCA(self, pot, bet, state, oppr, iter = 20):
        '''
        pot : chips won if opp FOLDS
        bet : chips needed to CALL

        STEP 1 : assuming FA, calculate opprc := call range # O(N) * O(logN)
        STEP 2 : compute FCA according to opprc             # O(N)
        STEP 3 : calculate opprc' := new call range         # O(NlogN)
        STEP 4 : opprc = avg(opprc, opprc')
        STEP 5 : GOTO STEP 2 ...

        Complexity  : O(NlogN * iter)
        ret         : v, myr, oppr
        '''

        # PRE
        fEV = state.wr(0)

        # STEP 1
        a, opprc, v = None, None, -1
        for i in range(self.nHands):
            pr, opprc2 = self.RP.rprob(i), self.Shoved(state, pot, i, r = oppr + 1)
            opppr = self.RP.rprob(opprc2) / self.RP.rprob(oppr)
            vh = (1 - pr) * fEV + \
                pr * (opppr * self.RP.rvr(i, opprc2) + (1 - opppr) * state.wr(pot + bet))
            if vh > v:
                a, opprc, v = i, opprc2, vh
        
        # STEP 2-5
        for it in range(1, iter):
            myr2 = np.array([0 for i in range(self.nHands)]) # 0, 1, 2 = F, C, A
            vh, opprc2 = 0, int(opprc)
            for i in range(self.nHands):
                cpr = self.RP.hvrEq(i, oppr) * self.pen
                cEV = cpr * state.wr(pot) + (1 - cpr) * state.wr(-bet)
                apr = self.RP.rprob(opprc2) / self.RP.rprob(oppr)
                aEV = apr * self.RP.hvr(i, opprc2) + (1 - apr) * state.wr(pot)
                best = max(fEV, cEV, aEV)
                if fEV == best:
                    myr2[i] = 0
                else:
                    myr2[i] = 2 if aEV == best else 1
                vh += self.RP.prob(i) * best

            opprc3 = self.Shovediscrete(state, pot, myr2 == 2, r = oppr + 1)
            opprc, v = (opprc * it + opprc3) / (it + 1), vh

        return v, myr2, opprc

    def Shoved(self, state, pot, oppr, l = 0, r = nHands):
        '''
        Calculate the range of calling allins, use binary search since linear range.
        Minimizes equity

        O(logN) for continuous range
        O(NlogN) for discrete range
        '''
        Feq = state.wr(pot)
        while r - l > 1:
            m = (l + r) // 2
            if self.RP.rvh(oppr, m) < Feq: l = m
            else: r = m
        return l

    def Shovediscrete(self, state, pot, oppr, l = 0, r = nHands):
        '''
        Calculate the range of calling allins, use binary search since linear range.
        Minimizes equity

        O(logN) for continuous range
        O(NlogN) for discrete range
        '''
        if oppr.any() == False: # no hand to shove
            return r
        Feq = state.wr(pot)
        while r - l > 1:
            m = (l + r) // 2
            if self.RP.hsvh(oppr, m) < Feq: l = m
            else: r = m
        return l
            

        

        
