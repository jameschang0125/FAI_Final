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
                if self.SBpaid * mult > thre:
                    self.EV += self.rp.fw * prob
                else:
                    WIN = self.state(self.SBpaid * mult) * self.rp.fw
                    LOSE = self.state(-self.BBpaid * mult) * self.rp.fq * (1 - self.rp.wr)
                    self.EV += (WIN + LOSE) * prob
            
            FEV1, FEV2 = self.state(self.SBpaid), self.state(-self.BBpaid)
            self.EV = np.maximum(FEV2, np.minimum(FEV1, self.EV))

    return _CALL

'''
be aware! this might make the raiser "get value" from weaker hands
'''
PRECALL = CALL #HERU((1, 0.7), (3, 0.3)) #((1, 0.75), (1.5, 0.1), (2, 0.1), (3, 0.05))
FLOPCALL = CALL # HERU((1, 0.8), (1.5, 0.1), (2, 0.05), (3, 0.05))
TURNCALL = CALL # HERU((1, 0.85), (1.5, 0.1), (2, 0.05))
RIVERCALL = CALL
