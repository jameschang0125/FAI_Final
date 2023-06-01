from pre.range_processer import RangeProcesser as RP
from eqcalc.state import State
import numpy as np

class researcher():
    '''
    This is a POSTFLOP (or PREFLOP 3B+) calculator.
    Suppose we have the range of BB and SB is given. 
    '''
    def __init__(self):
        # self.RP.nHands = 
        # self.RP

    def CR(self, pot, rsize, state):
        '''
            --- R --- F/A --- F/A
        ----
            --- C --- C/A --- F/A
        
        C/R with linear range

        In practice, we R with prob = 1 - slowp
        '''
        v, c, Rc, Cc, Ccc = 2, None, None, None, None
        for i in self.RP.nHands(BB = False):
            pr = self.RP.rprob(i, BB = False)
            REV, Rch = self.R_FA(pot, rsize, state, i) 
            CEV, Cch, Ccch = self.C_CA(pot, state, i)
            vh = pr * REV + (1 - pr) * CEV
            if vh < v:
                v, c, Rc, Cc, Ccc = vh, i, Rch, Cch, Ccch
        return v, c, Rc, Cc, Ccc
        
    def R_FA(self, pot, rsize, state, oppr):
        fEV = state.wr(0)
        v, c = -1, None
        for i in self.RP.nHands(BB = True):
            pr = self.RP.rprob(i, BB = True)
            opprc = self.Shoved(state, pot, oppr, l = 0, r = oppr)
            prc = self.RP.rprob_r(opprc, i, BB = False)
            acEV = self.RP.rvr(i, opprc)
            aEV = prc * acEV + (1 - prc) * state.wr(pot + rsize)
            vh = pr * aEV + (1 - pr) * fEV
            if vh > v:
                v, c = vh, i
        return v, c

    def C_CA(self, pot, state, oppr, slowp = 0.4):
        v, c, cc = -1, None, None
        if oppr = 0: oppr = self.RP.nHands(BB = False)
        for i in self.RP.nHands(BB = True):
            pr = self.RP.rprob(i, BB = True)
            opprc = self.Shoved(state, pot, oppr, l = 0, r = self.RP.nHands(BB = False))

            # case 1: slowp
            prc = self.RP.rprob_r(opprc, i, BB = False)
            acEVs = prc * self.RP.rvr(i, opprc) + (1 - prc) * state.wr(pot)
            
            # case 2 : not slowp
            # note : force called for top range in C ?
            opprc2 = min(opprc, oppr - 1)
            prc = self.RP.r2prob_r(opprc2, oppr - 1, i, BB = False) / self.RP.r2prob_r(0, oppr - 1, i, BB = False)
            acEVn = prc * self.RP.rvr2(i, opprc2, oppr - 1) + (1 - prc) * state.wr(pot)

            aEV = slowp * acEVs + (1 - slowp) * acEVn

            ceq = slowp * self.RP.r2vr(0, max(0, i - 1), self.RP.nHands(BB = False)) + \
                  (1 - slowp) * self.RP.r2vr2(0, max(0, i - 1), 0, max(0, oppr - 1))
            cEV = ceq * state.wr(pot) + (1 - ceq) * state.wr(0)

            vh = pr * aEV + (1 - pr) * cEV

            if vh > v:
                v, c, cc = vh, i, opprc

        return v, c, cc


        


        


        






