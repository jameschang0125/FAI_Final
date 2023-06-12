from itertools import product
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from eqcalc.state import State
from subagent.newclass import PreRangeProcesser as PRP
from eqcalc.deep import *
from subagent.heuristics import *
from tqdm import tqdm
from random import random
from util.shower import Shower
from collections import ChainMap # aggregate dict

class preflopper():
    def __init__(self, debug = False, hiru = None):
        self.debug = debug
        self.rp = PRP()
        self.eq = EQ()
        self.call = PRECALL if hiru is None else hiru

    def RTREE(self, x):
        return {
            RAISE(x, msg = f"R({x})"): {
                FOLD: None,
                self.call: None,
                **ALLINTREE
            }
        }
    
    def RTREE2(self, x):
        if 4 * x < 150:
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call: None,
                    **self.RTREE(3 * x),
                    **self.RTREE(4 * x),
                    **ALLINTREE
                }
            }
        if 3 * x < 150:
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call: None,
                    **self.RTREE(2 * x),
                    **self.RTREE(3 * x),
                    **ALLINTREE
                }
            }
        return self.RTREE(x)

    def RTREE3(self, xs):
        return ChainMap(*[self.RTREE2(x) for x in xs])
    
    def SB_default(self, cur):
        # a bit deep, but just for testing purpose
        return BLINDS(self.rp, cur, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE3(range(15, 36, 5)),
                **ALLINTREE
            },
            **self.RTREE3(range(15, 36, 5)),
            **ALLINTREE
        })

    def BB_default(self, cur, rsize):
        if rsize == 10 or rsize == 1: return self.SB_default(cur) # 1 = ALLIN
        return BLINDS(self.rp, cur, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE3(range(15, 36, 5)),
                **ALLINTREE
            },
            **self.RTREE2(rsize),
            **ALLINTREE
        })

    def act(self, BBchip, turn, myh, *actions, nIter = 250):
        '''
        actions: signatures, see eqcalc.deep
        ret : signature
        '''
        if self.debug: print(f"[DEBUG][preflop.py] {(BBchip, turn)} actions = {actions}")
        
        debug = self.debug
        cur = State(BBchip, turn = turn, equitizer = self.eq)
        if len(actions) >= 2:
            self.gt.lock(depth = len(actions) - 1)
            if self.gt.find(*actions) is None:
                ptr = self.gt.find(*(actions[:-1]))
                gt = self.RTREE2(actions[-1])
                ptr.addChild(gt)
        elif hasattr(self, 'gt'):
            pass
        elif len(actions) == 0:
            self.gt = self.SB_default(cur)
        elif len(actions) == 1:
            self.gt = self.BB_default(cur, actions[0])
        else:
            raise ValueError("[PREFLOP] called w/o gt!")
        
        self.gt.reset()
        loader = tqdm(range(nIter)) if debug else range(nIter)
        for i in loader:
            self.gt.update()
        
        ptr = self.gt.find(*actions)
        # isBB = len(actions) % 2 == 1
        myid = self.rp.h2i(myh)
        prob = ptr.actprob[:, myid]
        if debug:
            tmp = [c.signature for c in ptr.children]
            with np.printoptions(precision = 3, suppress = True):
                print(f"[DEBUG][postflop.act] choosing from {tmp} with p {prob}")
        if debug:
            if len(actions) > 0:
                ptr2 = self.gt.find(*(actions[:-1]))
                if not ptr2.term:  
                    print(f"[DEBUG][postflop.act] ptr2.children = {[c.signature for c in ptr2.children]}")
                    print(f"[DEBUG] opp. range:")
                    ptr2.show()
            if not ptr.term: 
                print(f"[DEBUG][postflop.act] ptr.children = {[c.signature for c in ptr.children]}")
                print(f"[DEBUG] my range:")
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


        



