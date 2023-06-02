from pre.range_processer import RangeProcesser as RP
from eqcalc.state import State
import numpy as np

class researcher():
    '''
    This is a POSTFLOP (or PREFLOP 3B+) calculator.
    Suppose we have the range of BB and SB is given.
    TODO: division by 0 
    '''
    def __init__(self, rp):
        self.RP = rp

    def CR(self, pot, rsize, state, pen = 0):
        '''
            --- R --- F/A --- F/A
        ----
            --- C --- C/A --- F/A
        
        C/R with linear range

        In practice, we R with prob = 1 - slowp
        pen : penalized (increases) call EV

        ret meanings
        v   : optimal wr(BB)
        c   : SB's best R range
        Rc  : BB's A range if SB R
        Cc  : BB's A range if SB C
        Ccc : SB's A range if BB A
        '''
        v, c, Rc, Rcc, Cc, Ccc = 2, None, None, None, None, None
        for i in range(2, self.RP.nHands(BB = False) - 2): # hot fix
            # print(f"--- {i} ---") # DEBUG
            pr = self.RP.rprob(i, BB = False)
            REV, Rch, Rcch = self.R_FA(pot, rsize, state, i) 
            CEV, Cch, Ccch = self.C_CA(pot, state, i)
            vh = pr * REV + (1 - pr) * (CEV + pen) / (1 + pen)
            # print(f"vh = {'%.5f'%vh}, pr(R) = {'%.5f'%pr}, REV = {'%.5f'%REV}, CEV = {'%.5f'%CEV}") # DEBUG
            if vh < v:
                v, c, Rc, Rcc, Cc, Ccc = vh, i, Rch, Rcch, Cch, Ccch
                
                # DEBUG
                bestREV, bestCEV = REV, CEV
        
        # DEBUG
        '''
        print(f"C penalty            : {pen}")
        print(f"optimal wr(BB)       : {v}")
        print(f"SB's best R range    : {c}")
        print(f"R - A                : {Rc}")
        print(f"R - A - A            : {Rcc}")
        print(f"C - A                : {Cc}")
        print(f"C - A - A            : {Ccc}")
        print(f"EV when SB R         : {bestREV}")
        print(f"EV when SB C         : {bestCEV}")
        '''

        return v, c, Rc, Cc, Ccc
    
    def R_MDF(self, pot, rsize, state, aggr = 0.9):
        '''
        We will compute the MDF such that the bottom range of R cannot gain freely
        '''
        bot = self.RP.nHands(BB = False) - 1
        for i in range(self.RP.nHands(BB = True)):
            mypr = self.RP.rprob(i, BB = True) # not acc. but nvm
            SB_bot_rEV = mypr * state.wr(pot + rsize) + (1 - mypr) * state.wr(0)

            eq = self.RP.rvh(self.RP.nHands(BB = True) - 1, bot) ## BB eq
            SB_bot_cEV = state.wr(pot) * eq + state.wr(0) * (1 - eq)

            if SB_bot_cEV < SB_bot_rEV: # call is better, since SB minimizes
                return int(i * aggr)

        return 0 # in this case, SB's range is too good

    def R_FA(self, pot, rsize, state, oppr):
        fEV = state.wr(0)
        v, c, cc = -1, None, None

        mdf = self.R_MDF(pot, rsize, state)
        # print(f"mdf = {mdf}")

        for i in range(mdf, self.RP.nHands(BB = True)):
            pr, vh = self.RP.rprob(i, BB = True), -1
            tmp = self.RP.rprob_r(oppr, i, BB = True)
            if tmp > 0:
                opprc = self.Shoved(state, pot + rsize, i, l = 0, r = oppr + 1)   
                prc = self.RP.rprob_r(opprc, i, BB = True) / tmp
                acEV = self.RP.rvr(i, opprc)
                aEV = prc * acEV + (1 - prc) * state.wr(pot + rsize)
                vh = pr * aEV + (1 - pr) * fEV

                # if oppr == 2: print(f"{i} :: vh = {vh}, opprc = {opprc}, pr = {pr}, aEV = {aEV}, fEV = {fEV}")
            # NOTE: tmp == 0 is actually quite common when oppr and i are both small
            # since strong ranges overlaps a lot
            if vh > v:
                v, c, cc = vh, i, opprc
        return v, c, cc

    def C_A_MDF(self, pot, state, oppr, slowp, aggr = 1):
        '''
        We will compute the MDF such that the bottom range of BB cannot gain freely
        oppr : actually myr
        '''
        bot = self.RP.nHands(BB = True) - 1
        for i in range(self.RP.nHands(BB = False)):
            mypr = self.RP.rprob(i, BB = False) # not acc. but nvm
            BB_bot_rEVs = mypr * self.RP.hvr(bot, i) + (1 - mypr) * state.wr(pot)
            
            BB_bot_rEVn = state.wr(pot)
            if i < oppr + 1 and oppr + 1 < self.RP.nHands(BB = False):
                mypr = self.RP.r2prob(oppr + 1, i, BB = False) / self.RP.r2prob(oppr + 1, self.RP.nHands(BB = False) - 1, BB = False)
                BB_bot_rEVn = mypr * self.RP.hvr2(bot, oppr + 1, i) + (1 - mypr) * state.wr(pot)

            BB_bot_rEV = BB_bot_rEVs * slowp + BB_bot_rEVn * (1 - slowp)

            eq = self.RP.hvr(bot, self.RP.nHands(BB = False) - 1) * slowp
            if oppr + 1 < self.RP.nHands(BB = False):
                eq += self.RP.hvr2(bot, oppr + 1, self.RP.nHands(BB = False) - 1) * (1 - slowp)
            else: eq += 1 - slowp

            BB_bot_cEV = state.wr(pot) * eq + state.wr(0) * (1 - eq)
            
            if BB_bot_cEV > BB_bot_rEV: # call is better, since BB maximizes
                return min(int(i * aggr), self.RP.nHands(BB = False) - 1)

        return 0 # in this case, BB's range is too good

    def C_CA(self, pot, state, oppr, slowp = 0.4, award = 1):
        v, c, cc = -1, None, None

        mdf = self.C_A_MDF(pot, state, oppr, slowp)

        for i in range(self.RP.nHands(BB = True)):
            pr = self.RP.rprob(i, BB = True)
            opprc = self.Shoved(state, pot, i, l = 0, r = self.RP.nHands(BB = False))
            opprc = max(mdf, opprc)

            # if oppr == 47: print(f"{i} :: ")

            # case 1: slowp
            prc = self.RP.rprob_r(opprc, i, BB = True)
            acEVs = prc * self.RP.rvr(i, opprc) + (1 - prc) * state.wr(pot)
            
            # if oppr == 47: print(f"opprc = {opprc}, prc = {prc}, acEVs = {acEVs}")

            # case 2 : not slowp
            # note : force called for top range in C ?
            acEVn = state.wr(pot)
            if opprc >= oppr + 1:
                tmp = self.RP.r2prob_r(oppr + 1, self.RP.nHands(BB = False) - 1, i, BB = False)
                if tmp == 0:
                    prc = 0
                else:
                    prc = self.RP.r2prob_r(oppr + 1, opprc, i, BB = False) / tmp
                acEVn = prc * self.RP.rvr2(i, oppr + 1, opprc) + (1 - prc) * state.wr(pot)

            aEV = slowp * acEVs + (1 - slowp) * acEVn

            # if oppr == 47: print(f"aEV = {aEV}, acEVn = {acEVn}")

            ceq = 1
            if i < self.RP.nHands(BB = True) and oppr < self.RP.nHands(BB = False):
                # else irrelevant
                ceq += slowp * self.RP.r2vr(i + 1, self.RP.nHands(BB = True) - 1, self.RP.nHands(BB = False) - 1)
                ceq += (1 - slowp) * self.RP.r2vr2(i + 1, self.RP.nHands(BB = True) - 1, oppr + 1, self.RP.nHands(BB = False) - 1)
                ceq *= award
            cEV = ceq * state.wr(pot) + (1 - ceq) * state.wr(0)
            
            vh = pr * aEV + (1 - pr) * cEV

            #if oppr == 47: 
            #    print(f"vh = {'%.5f'%vh}, pr(R) = {'%.5f'%pr}, aEV = {'%.5f'%aEV}, cEV = {'%.5f'%cEV}") # DEBUG
            

            if vh > v:
                v, c, cc = vh, i, opprc

        return v, c, cc

    def Shoved(self, state, pot, oppr, l = 0, r = None):
        '''
        minimize ev
        '''
        if r is None: return 0
        fEV = state.wr(pot)
        for i in range(l, r):
            cEV = self.RP.rvh(oppr, i)

            if fEV < cEV: # fold is better
                return max(0, i - 1)
        return r - 1
        

        
        


        


        






