from itertools import product
from src.eqcalc.state import State
from src.pre.equireader import Equireader as EQ
from src.eqcalc.state import State
from src.subagent.newclass import PreRangeProcesser as PRP
from src.eqcalc.deep import *
from src.subagent.heuristics import *
from tqdm import tqdm
from random import random
from src.util.shower import Shower
from collections import ChainMap # aggregate dict

class preflopper():
    def __init__(self, debug = False, heur = None):
        self.debug = debug
        self.rp = PRP()
        self.eq = EQ()
        self.call = CALL if heur is None else heur
    
    def RTREE(self, x, BB = False):
        if x > self.cur.thre(BB): return ALLINTREE
        return {
            RAISE(x, msg = f"R({x})"): {
                FOLD: None,
                self.call: None,
                **ALLINTREE
            }
        }
    
    def RTREE2(self, x, BB = False):
        if x > self.cur.thre(BB): return ALLINTREE
        if 4 * x <= self.cur.thre(not BB):
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call: None,
                    **self.RTREE(3 * x, not BB),
                    **self.RTREE(4 * x, not BB),
                    **ALLINTREE
                }
            }
        if 3 * x <= self.cur.thre(not BB):
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call: None,
                    **self.RTREE(2 * x, not BB),
                    **self.RTREE(3 * x, not BB),
                    **ALLINTREE
                }
            }
        if 2 * x <= self.cur.thre(not BB):
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call: None,
                    **self.RTREE(2 * x, not BB),
                    **ALLINTREE
                }
            }
        return self.RTREE(x, BB)

    def RTREE3(self, xs, BB = True):
        return ChainMap(*[self.RTREE2(x, BB = BB) for x in xs])
    
    def SB_default(self, cur):
        # a bit deep, but just for testing purpose
        if cur.othre(BB = False) < 10: return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            **ALLINTREE
        })
        return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE3(range(15, min(36, cur.thre(BB = True) + 1), 5), BB = True),
                **ALLINTREE
            },
            **self.RTREE3(range(15, min(36, cur.thre(BB = False) + 1), 5), BB = False),
            **ALLINTREE
        })

    def BB_default(self, cur, rsize):
        if rsize == 10 or rsize == 1 or rsize > cur.thre(BB = False): return self.SB_default(cur) # 1 = ALLIN
        return BLINDS(self.rp, self.nxt, {
            FOLD: None,
            LIMP: {
                self.call: None,
                **self.RTREE3(range(15, min(36, cur.thre(BB = True) + 1), 5), BB = True),
                **ALLINTREE
            },
            **self.RTREE2(rsize, BB = False),
            **ALLINTREE
        })

    def transform(self, xs, cur):
        ans, BB = [], False
        for x in xs:
            ans.append(x if x <= cur.thre(BB = BB) else 1)
            BB = not BB
        return ans

    def act(self, BBchip, turn, myh, *actions, nIter = 130, verbose = False):
        '''
        actions: signatures, see eqcalc.deep
        ret : signature
        '''
        cur = State(BBchip, turn = turn, equitizer = self.eq)
        nxt = cur.to()
        self.cur, self.nxt = cur, nxt
        actions = self.transform(actions, cur)
        if self.debug: 
            print(f"[DEBUG][preflop.py] {(BBchip, turn)} actions = {actions}, cur.thre = {cur.thre()}")
        
        debug = self.debug
        if len(actions) >= 2:
            isBB = len(actions) % 2 == 1
            self.gt.lock(depth = len(actions) - 1)
            if self.gt.find(*actions) is None:
                ptr = self.gt.find(*(actions[:-1]))
                gt = self.RTREE2(actions[-1], BB = not isBB)
                ptr.addChild(gt)
        elif hasattr(self, 'gt'):
            pass
        elif len(actions) == 0:
            # edge case: FOLD = LOSE
            if cur.thre(BB = False) < 10: return 1

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
                print(f"[DEBUG][preflop.act] choosing from {tmp} with p {prob}")
            if len(actions) > 0:
                ptr2 = self.gt.find(*(actions[:-1]))
                if not ptr2.term:  
                    print(f"[DEBUG][preflop.act] ptr2.children = {[c.signature for c in ptr2.children]}")
                    print(f"[DEBUG] opp. range:")
                    ptr2.show(verbose = verbose)
            if not ptr.term: 
                print(f"[DEBUG][preflop.act] ptr.children = {[c.signature for c in ptr.children]}")
                print(f"[DEBUG] my range:")
                ptr.show(verbose = verbose)
        
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
        actions = self.transform(actions, self.cur)
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


        



