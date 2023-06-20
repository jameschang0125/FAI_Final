from src.subagent.postflop import postflopper
from src.eqcalc.deep import *
from collections import ChainMap # aggregate dict
from src.subagent.heuristics import *

class SPostflopper(postflopper):
    def __init__(self, *args, betportions = [0.33, 0.6, 0.8, 1.3],
                 raiseportions = [0.85, 0.67, 0.5, 0.33], **kwargs):
        super().__init__(*args, **kwargs)
        self.betportions = betportions
        self.raiseportions = raiseportions

    def clip(self, xs, u):
        ans = []
        for x in xs:
            if x <= u: ans.append(x)
        return ans
    
    def rrange(self, u):
        if u < 10: return []
        ans = [10]
        for c in self.betportions:
            tmp = int(c * self.pot)
            if 10 < tmp <= u: ans.append(tmp)
        return ans

    def RTREE2(self, x, street = STREETFLOP, BB = False):
        u = min(self.cur.thre(False), self.cur.thre(True)) - self.pot / 2
        for c in self.raiseportions:
            tmp = int(x + (self.pot + 2 * x) * c)
            if tmp <= u:
                return {
                    RAISE(x, msg = f"R({x})"): {
                        FOLD: None,
                        self.call[street]: None,
                        **self.RTREE(tmp, street = street, BB = not BB),
                        **ALLINTREE
                    }
                }
        return self.RTREE(x, BB = BB)

    def SB_default(self, cur, pot, street = STREETFLOP):
        return POT(pot)(self.rp, self.nxt, {
            CHECK: {
                self.call[street]: None,
                **self.RTREE3(self.rrange(cur.thre(BB = True)), street, BB = True),
                **ALLINTREE
            },
            **self.RTREE3(self.rrange(cur.thre(BB = False)), street, BB = False),
            **ALLINTREE
        })

    def BB_default(self, cur, pot, rsize, street = STREETFLOP):
        if rsize == 0 or rsize == 1 or rsize + pot / 2 > cur.thre(BB = False): 
            return self.SB_default(cur, pot, street = street)
        return POT(pot)(self.rp, self.nxt, {
            CHECK: {
                self.call[street]: None,
                **self.RTREE3(self.rrange(cur.thre(BB = True)), street, BB = True),
                **ALLINTREE
            },
            **self.RTREE2(rsize, street, BB = False),
            **ALLINTREE
        })