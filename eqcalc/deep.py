from eqcalc.search import searcher
import numpy as np

class DeepSearcher(searcher):
    '''
    This evaluates more actions.
    Too complex to be evaluated run-time.
    All ranges are represented in 169 * 2 : P(C/R), P(A)
    '''
    # nHands = 13 * 13
    
    def __init__(self):
        super().__init__()
    
    def FRA(self, state, rsize, iter = 100):
        '''
        Initialize FRA strategy using (FR + FA) / 2
        Compute optimal FCA strategy agianst
        Compute optimal FRA & FC strategy against...

        oppr : best against C
        '''
        fEV = state.wr(self.BB)

        v0, a0, c0, cc0 = self.FR(rsize, state, verbose = True)
        v1, a1, c1 = self.FR(1000, state)

        myr = np.array([[0.5 if i < a0 else 0], [0.5 if i < a1 else 0]])
        oppr = np.array([[1 if c0 == 1 else 0], [1 if c0 == 2 else 0]])
        mya, oppa = cc0, np.sum(c1 == 2) # against ALLIN

        for it in range(1, iter):
            vo, oppr2, oppa2, mya2 = self.FRA_FCA(state, rsize, myr)
            myr2 = np.zeros((2, self.nHands))
            '''
            for i in range(self.nHands):
                # R
                p_RF = 
                e_RF = state.wr(0)
                p_RC = 
                e_RC = 
                p_RA = 
                e_RA = 
                rEV =
                # A
                apr = self.RP.rprob(oppra)
                aEV = apr * self.RP.hvr(i, oppra) + (1 - apr) * state.wr(0)
            '''


    def FRA_FC(self, state, rsize):
        pass
    
    def FRA_FCA(self, state, rsize):
        pass

    def FRA_FR(self, state, sbrsize, bbrsize):
        pass

    def FRA_FR_FA(self, state, sbrsize, bbrsize):
        pass


