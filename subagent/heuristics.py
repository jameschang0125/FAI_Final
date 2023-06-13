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

            for mult, prob in dist:
                WIN = self.state(self.SBpaid * mult) * self.rp.fw
                LOSE = self.state(-self.BBpaid * mult) * self.rp.fq * (1 - self.rp.wr)
                self.EV += (WIN + LOSE) * prob
    return _CALL

PRECALL = HERU((1, 0.7), (1.5, 0.1), (2, 0.1), (3, 0.1))
FLOPCALL = HERU((1, 0.7), (1.5, 0.1), (2, 0.1), (10, 0.1))
TURNCALL = HERU((1, 0.8), (1.5, 0.1), (2, 0.1))
RIVERCALL = CALL
