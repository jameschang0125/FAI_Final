from eqcalc.deep import *

STREETFLOP = 0
STREETTURN = 1
STREETRIVER = 2

def HERU(*dist):
    '''
    dist: [(multiplier, prob)], prob must sum to 1
    '''
    class _CALL(CALL):
        def __init__(self, gt, ct = None, **kwargs):
            super().__init__(gt, **kwargs)
            self.EV = np.zeros(self.rp.wr.shape)

            assert(self.SBpaid - self.BBpaid < 1e-6)
            thre = self.state.thre()

            for mult, prob in dist:
                WIN = self.state(self.SBpaid * mult) * self.rp.fw
                LOSE = self.state(-self.BBpaid * mult) * self.rp.fq * (1 - self.rp.wr)
                self.EV += (WIN + LOSE) * prob
            
            FEV1, FEV2 = self.state(self.SBpaid) * self.rp.fq, self.state(-self.BBpaid) * self.rp.fq
            self.EV = np.maximum(FEV2, np.minimum(FEV1, self.EV))

    return _CALL

'''
be aware! this might make the raiser "get value" from weaker hands
'''
PRECALL = HERU((1, 0.85), (1.5, 0.05), (2, 0.05), (3, 0.05))
FLOPCALL = HERU((1, 0.8), (1.5, 0.1), (2, 0.05), (3, 0.05))
TURNCALL = HERU((1, 0.85), (1.5, 0.1), (2, 0.05))

PRECALL2 = HERU((1, 0.9), (1.5, 0.05), (2, 0.03), (3, 0.02))
FLOPCALL2 = HERU((1, 0.9), (1.5, 0.05), (2, 0.03), (3, 0.02))
TURNCALL2 = HERU((1, 0.95), (1.5, 0.03), (2, 0.02))

PRECALL3 = HERU((1, 0.78), (1.5, 0.1), (2, 0.07), (3, 0.05))
FLOPCALL3 = HERU((1, 0.78), (1.5, 0.1), (2, 0.07), (3, 0.05))
TURNCALL3 = HERU((1, 0.9), (1.5, 0.05), (2, 0.05))

PRECALL4 = HERU((1, 0.85), (1.5, 0.07), (2, 0.05), (3, 0.03))
FLOPCALL4 = HERU((1, 0.84), (1.5, 0.08), (2, 0.05), (3, 0.03))
TURNCALL4 = HERU((1, 0.9), (1.5, 0.05), (2, 0.05))

FLOPCALL5 = HERU((1, 0.94), (1.5, 0.03), (2, 0.02), (3, 0.01))
TURNCALL5 = CALL

RIVERCALL = CALL
