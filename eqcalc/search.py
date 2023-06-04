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

    def __init__(self, prepen = 0.95, **kwargs):
        self.RP = RP()
        self.pen = prepen

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

    @classmethod
    def hs2s(self, hs):
        return [self.h2s(h) for h in hs]

    def i2s(self, i):
        '''
        id to string
        '''
        return self.h2s(self.i2h(i))

    def is2s(self, i):
        '''
        id to string
        '''
        return [self.i2s(j) for j in i]
    
    def r2s(self, r):
        sols = np.where(r == 2)[0]
        return [self.i2s(id) for id in sols]

    def i2h(self, i):
        return self.RP.i2h[i]

    def h2i(self, h):
        return self.RP.h2i[h]
    
    def h2h(self, h):
        x, y = h
        m, n = x[1] - 2, y[1] - 2
        m, n = max(m, n), min(m, n)
        if x[0] == y[0]: m, n = n, m
        return m + n * 13
        '''
        x, y = h
        m, n = x.rank - 2, y.rank - 2
        m, n = max(m, n), min(m, n)
        if x.suit == y.suit: m, n = n, m
        return m + n * 13
        '''
    
    def h2h2i(self, h):
        return self.h2i(self.h2h(h))

    def AoF(self, state, iter = 301):
        '''
        calculate almost exact Nash. (probably) need to be precomputed.

        O(NN * iter ~ 8.6M), about 12s 
        '''
        v, a, c = self.FR(1000, state)

        # DEBUG
        np.set_printoptions(precision = 3, suppress = True)

        myr, oppr = np.zeros((self.nHands)), np.zeros((self.nHands))
        for i in range(self.nHands):
            myr[i] = int(c[1][i] + c[0][i] > 0.5)
            oppr[i] = int(i <= a)
        
        #print(myr)
        #print(oppr)

        lr, decay = 0.8, 0.97 # 0.8 * 0.97 ** 200 ~ 0.5%
        for it in range(1, iter):
            '''
            if it % 40 == 0:
                print(f"\n---- iter {it} ----")
                print(myr)
                print(oppr)
            '''

            myr2, oppr2 = self.AoF_iter(state, myr, oppr, it)
            myr = myr2 * (1 - lr) + myr * lr
            oppr = oppr2 * (1 - lr) + oppr * lr
        
        # calculate eq
        val = 0
        fEV, sfEV = state.wr(0), state.wr(15)
        for i in range(self.nHands):
            for j in range(self.nHands):
                tmp = (1 - oppr[j]) * sfEV 
                tmp += oppr[j] * (myr[i] * self.RP.hvh(i, j) + (1 - myr[j]) * fEV)
                val += tmp * self.RP.combprob(i, j)

        return val, myr, oppr

    def AoF_iter(self, state, myr, oppr, it = None):
        # SB BR
        fEV, sfEV = state.wr(0), state.wr(15)
        oppr2 = np.zeros(self.nHands)
        for i in range(self.nHands):
            aEV = 0
            for j in range(self.nHands): # opp
                pr = self.RP.combprob(j, i)
                if pr == 0: continue
                tmp = myr[j] * self.RP.hvh(j, i) + (1 - myr[j]) * fEV
                aEV += tmp * pr
            fEV2 = sfEV * self.RP.prob(j) 
            oppr2[i] = 1 if aEV < fEV2 else 0

        # BB BR
        myr2 = np.zeros(self.nHands)
        for i in range(self.nHands):
            aEV, tprob = 0, 0
            for j in range(self.nHands): # opp
                pr = self.RP.combprob(i, j)
                if pr == 0: continue
                tprob += pr * oppr[j]
                aEV += pr * oppr[j] * self.RP.hvh(i, j)
            fEV2 = fEV * tprob
            # if it % 40 == 0: print(f"#{i} : aEV = {'%.5f'%aEV}, fEV = {'%.5f'%fEV2}")
            myr2[i] = 1 if aEV > fEV2 else 0
        
        return myr2, oppr2


            



    def FR(self, bet, state, verbose = False):
        '''
        bet : bet size for SB
        '''

        # PRE
        fEV = state.wr(self.BB * 1.5)
        if verbose: print(f"fEV = {fEV}")

        vac = []
        for i in list(range(0, self.nHands, 10)) + [self.nHands - 1]:
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
        return (v, a, c, cc) if verbose else (v, a, c)

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
            opppr = self.RP.rprob_r(opprc2, i) / self.RP.rprob_r(oppr, i)
            vh = (1 - pr) * fEV + \
                pr * (opppr * self.RP.rvr(i, opprc2) + (1 - opppr) * state.wr(pot + bet))
            if vh > v:
                a, opprc, v = i, opprc2, vh
        
        # STEP 2-5

        tmp = np.zeros((2, self.nHands))
        for it in range(1, iter):
            myr2 = np.array([0 for i in range(self.nHands)]) # 0, 1, 2 = F, C, A
            vh, opprc2 = 0, int(opprc)

            for i in range(self.nHands):
                cpr = self.RP.hvrEq(i, oppr) * self.pen
                cEV = cpr * state.wr(pot) + (1 - cpr) * state.wr(-bet)
                apr = self.RP.rprob_h(opprc2, i) / self.RP.rprob_h(oppr, i)
                aEV = apr * self.RP.hvr(i, opprc2) + (1 - apr) * state.wr(pot)
                best = max(fEV, cEV, aEV)
                if fEV == best:
                    myr2[i] = 0
                else:
                    myr2[i] = 2 if aEV == best else 1
                vh += self.RP.prob(i) * best
                
                # DEBUG
                # if oppr == self.nHands - 1 and it == iter - 1:
                #    print(f"with hand {self.i2s(i)}, cEV = {cEV}, aEV = {aEV}, fEV = {fEV}")

            tmp[0] += myr2 == 1
            tmp[1] += myr2 == 2

            # DEBUG
            '''
            if oppr == self.nHands - 1:
                tmp[0] += myr2 == 1
                tmp[1] += myr2 == 2
                print(tmp / it)
                if it == iter - 1:
                    print(f"opponent calling shove with {self.is2s(range(opprc2 + 1))}")
            '''
            opprc3 = self.Shovediscrete(state, pot, myr2 == 2, r = oppr + 1)
            opprc, v = (opprc * it + opprc3) / (it + 1), vh

        return v, tmp / (iter - 1), opprc # v, myr2, opprc

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
            

        

        
