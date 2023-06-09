from itertools import product
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from eqcalc.state import State
from subagent.newclass import PreRangeProcesser as PRP
from eqcalc.deep import *
from tqdm import tqdm
from random import random
from util.shower import Shower

class preflopper():
    def __init__(self, debug = False):
        self.debug = debug
        self.rp = PRP()
        self.eq = EQ()
    
    def SB_default(self, cur):
        # a bit deep, but just for testing purpose
        return BLINDS(self.rp, cur, {
            FOLD: None,
            LIMP: {
                CALL: None,
                **{
                RAISE(i, msg = f"R({i})"): {
                    FOLD: None,
                    CALL: None,
                    ALLIN: {
                        FOLD: None,
                        CALLIN: None
                    }
                } for i in range(15, 36, 5)}
            },
            **{
            RAISE(i, msg = f"R({i})"): {
                FOLD: None,
                CALL: None,
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            } for i in range(15, 36, 5)},
            ALLIN: {
                FOLD: None,
                CALLIN: None
            }
        })

    def BB_default(self, cur, rsize):
        if rsize == 10 or rsize == 1: return self.SB_default(cur) # 1 = ALLIN
        return BLINDS(self.rp, cur, {
            FOLD: None,
            LIMP: {
                CALL: None,
                **{
                RAISE(i, msg = f"R({i})"): {
                    FOLD: None,
                    CALL: None,
                    ALLIN: {
                        FOLD: None,
                        CALLIN: None
                    }
                } for i in range(15, 36, 5)}
            },
            RAISE(rsize): {
                FOLD: None,
                CALL: None,
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            },
            ALLIN: {
                FOLD: None,
                CALLIN: None
            }
        })

    def raisetree(self, x):
        return {
            RAISE(x): {
                FOLD: None,
                CALL: None,
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            }
        }

    def act(self, BBchip, turn, myh, *actions, nIter = 250):
        '''
        actions: signatures, see eqcalc.deep
        ret : signature
        '''
        if self.debug: print(f"[DEBUG][preflop.py] actions = {actions}")
        
        debug = self.debug
        cur = State(BBchip, turn = turn, equitizer = self.eq)
        if len(actions) == 0:
            self.gt = self.SB_default(cur)
        elif len(actions) == 1:
            self.gt = self.BB_default(cur, actions[0])
        elif len(actions) == 2: # C - R or R - 3B
            self.gt.lock(depth = 2)
            if self.gt.find(*actions) is None:
                ptr = self.gt.find(*(actions[:-1]))
                gt = self.raisetree(actions[-1])
                ptr.addChild(gt)
        elif len(actions) == 3: # C - R - 3B
            self.gt.lock(depth = 3)
            if self.gt.find(*actions) is None:
                ptr = self.gt.find(*(actions[:-1]))
                gt = self.raisetree(actions[-1])
                ptr.addChild(gt)
        else:
            raise RuntimeError
        
        self.gt.reset()
        loader = tqdm(range(nIter)) if debug else range(nIter)
        for i in loader:
            self.gt.update()
        
        ptr = self.gt.find(*actions)
        # isBB = len(actions) % 2 == 1
        myid = self.rp.h2i(myh)
        prob = ptr.actprob[:, myid]
        if debug:
            ptr.show()
        # TODO: add activation function?
        action = np.random.choice(np.arange(len(prob)), p = prob)
        return ptr.children[action].signature

    def norm(self, x):
        return x / np.max(x)

    def sampleFrom(self, BBp, BB = True, eps = 0.02):
        BBh = self.rp.nHands(BB = True) if BB else self.rp.nHands(BB = False)
        BBr = []
        for i in range(BBh):
            x = self.rp.i2h(i, BB = BB)
            for h in x:
                if random() < BBp[i] + eps: BBr.append(h)
        return BBr
    
    def sample(self, p, BB = True, eps = 0.02, minSamples = 100):
        cnt, BBr, ieps = 0, self.sampleFrom(p, BB, eps), eps
        while cnt < 10 and len(BBr) < minSamples:
            cnt += 1
            p, ieps = p ** 0.8, ieps + 0.5 * eps
            BBr = self.sampleFrom(p, BB, eps)
        return BBr

    def ranges(self, myh, *actions, eps = 0.02, minSamples = 100):
        '''
        given an action line, output (could be a sample) of BBr, SBr
        '''
        if self.debug: 
            print(f"[DEBUG][preflop.ranges] actions = {actions}")
            print(f"[DEBUG][preflop.ranges] gt.getTree = {self.gt.getTree()}")
        
        BBp, SBp = self.gt.condprob(*actions)
        BBp, SBp = self.norm(BBp), self.norm(SBp)

        if self.debug:
            with np.printoptions(precision = 3, suppress = True):
                print(f"[DEBUG][preflop.ranges] BBp, SBp = \n{BBp}\n{SBp}")

        BBr, SBr = self.sample(BBp, True, eps, minSamples), self.sample(SBp, False, eps, minSamples)
        
        if self.debug:
            print(f"[DEBUG][preflop.ranges]: \nBBr = {Shower.hs2s(BBr)}\nSBr = {Shower.hs2s(SBr)}")

        return BBr, SBr


        



