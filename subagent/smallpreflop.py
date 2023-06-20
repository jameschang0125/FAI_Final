from subagent.preflop import preflopper
from eqcalc.deep import *
from collections import ChainMap # aggregate dict
from subagent.heuristics import *

class SPreflopper(preflopper):
    def __init__(self, *args, raiseportions = [0.85, 0.67, 0.5, 0.33], **kwargs):
        super().__init__(*args, **kwargs)
        self.raiseportions = raiseportions
    
    def rrange(self, u, **kwargs):
        if u >= 45: return [20, 25, 35, 45]
        if u >= 35: return [15, 20, 25, 35]
        return range(15, u + 1, 5)
    
    def RTREE2(self, x, BB = False):
        u = min(self.cur.thre(False), self.cur.thre(True))
        for c in self.raiseportions:
            tmp = int(x + 2 * x * c)
            if tmp <= u:
                return {
                    RAISE(x, msg = f"R({x})"): {
                        FOLD: None,
                        self.call: None,
                        **self.RTREE(tmp, BB = not BB),
                        **ALLINTREE
                    }
                }
        return self.RTREE(x, BB = BB)
    
    def SB_default(self, cur):
        # a bit deep, but just for testing purpose
        if cur.othre(BB = False) < 10: return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            **ALLINTREE
        })

        u = min(self.cur.thre(False), self.cur.thre(True))
        return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE3(self.rrange(u, BB = True), BB = True),
                **ALLINTREE
            },
            **self.RTREE3(self.rrange(u, BB = False), BB = False),
            **ALLINTREE
        })

    def BB_default(self, cur, rsize):
        if rsize == 10 or rsize == 1 or rsize > cur.thre(BB = False): return self.SB_default(cur) # 1 = ALLIN
        return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE3(self.rrange(cur.thre(BB = True), BB = True), BB = True),
                **ALLINTREE
            },
            **self.RTREE2(rsize, BB = False),
            **ALLINTREE
        })

    def LimpRaiseTree(self, cur, rsize1, rsize2):
        if rsize1 is None:
            return BLINDS(self.rp, self.nxt, {
                FOLD: None,
                LIMP: {
                    self.call: None,
                    **self.RTREE2(rsize2, BB = True),
                    **ALLINTREE
                },
                **ALLINTREE
                })
        return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE2(rsize2, BB = True),
                **ALLINTREE
            },
            **self.RTREE2(rsize1, BB = False),
            **ALLINTREE
            })
