from itertools import product
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from eqcalc.state import State
from subagent.newclass import PostRangeProcesser as PRP
from eqcalc.deep import *
from subagent.heuristics import *
from tqdm import tqdm
from random import random
from util.shower import Shower
from collections import ChainMap # aggregate dict

class postflopper():
    def __init__(self, *args, debug = False, heur = None, **kwargs):
        # BBr, SBr, comm, BBincl = None, SBincl = None
        self.debug = debug
        self.rp = PRP(*args, **kwargs)
        self.eq = EQ()

        self.call = [CALL, CALL, CALL] if heur is None else heur
    
    def RTREE(self, x, street = STREETFLOP, BB = False):
        if x + self.pot / 2 > self.cur.thre(BB = BB): return ALLINTREE
        return {
            RAISE(x, msg = f"R({x})"): {
                FOLD: None,
                self.call[street]: None,
                **ALLINTREE
            }
        }
    
    def RTREE2(self, x, street = STREETFLOP, BB = False):
        if 4 * x + self.pot / 2 <= self.cur.thre(BB = BB):
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call[street]: None,
                    **self.RTREE(3 * x, street = street, BB = not BB),
                    **self.RTREE(4 * x, street = street, BB = not BB),
                    **ALLINTREE
                }
            }
        if 3 * x + self.pot / 2 <= self.cur.thre(BB = BB):
            return {
                RAISE(x, msg = f"R({x})"): {
                    FOLD: None,
                    self.call[street]: None,
                    **self.RTREE(2 * x, street = street, BB = not BB),
                    **self.RTREE(3 * x, street = street, BB = not BB),
                    **ALLINTREE
                }
            }
        return self.RTREE(x, BB = BB)

    def RTREE3(self, xs, street = STREETFLOP, BB = False):
        return ChainMap(*[self.RTREE2(x, street, BB) for x in xs])

    def SB_default(self, cur, pot, street = STREETFLOP):
        # a bit deep, but just for testing purpose
        return POT(pot)(self.rp, self.nxt, {
            CHECK: {
                self.call[street]: None,
                **self.RTREE3(range(10, min(61, cur.thre(BB = True) + 1 - int(pot / 2)), 5), street, BB = True),
                **ALLINTREE
            },
            **self.RTREE3(range(10, min(61, cur.thre(BB = False) + 1 - int(pot / 2)), 5), street, BB = False),
            **ALLINTREE
        })

    def BB_default(self, cur, pot, rsize, street = STREETFLOP):
        if rsize == 0 or rsize == 1 or rsize + pot / 2 > cur.thre(BB = False): 
            return self.SB_default(cur, pot, street = street)
        return POT(pot)(self.rp, self.nxt, {
            CHECK: {
                self.call[street]: None,
                **self.RTREE3(range(10, min(61, cur.thre(BB = True) + 1 - int(pot / 2)), 5), street, BB = True),
                **ALLINTREE
            },
            **self.RTREE2(rsize, street, BB = False),
            **ALLINTREE
        })

    def transform(self, xs, cur, pot):
        ans, BB = [], False
        for x in xs:
            ans.append(x if x + pot / 2 <= cur.thre(BB = BB) else 1)
            BB = not BB
        return ans

    def act(self, BBchip, turn, myh, pot, *actions, street = STREETFLOP, nIter = 160):
        '''
        actions: signatures, see eqcalc.deep
        ret : signature
        '''
        debug = self.debug
        cur = State(BBchip, turn = turn, equitizer = self.eq)
        self.cur, self.nxt, self.pot = cur, cur.to(), pot
        actions = self.transform(actions, cur, pot)
        isBB = len(actions) % 2 == 1

        if len(actions) >= 2:
            self.gt.lock(depth = len(actions) - 1)
            if self.gt.find(*actions) is None:
                ptr = self.gt.find(*(actions[:-1]))
                gt = self.RTREE2(actions[-1], BB = not isBB)
                ptr.addChild(gt)
        elif hasattr(self, 'gt'):
            pass
        elif len(actions) == 0:
            self.gt = self.SB_default(cur, pot, street = street)
        elif len(actions) == 1:
            self.gt = self.BB_default(cur, pot, actions[0], street = street)
        else:
            raise ValueError("[PREFLOP] called w/o gt!")
        
        self.gt.reset()
        loader = tqdm(range(nIter)) if debug else range(nIter)
        for i in loader:
            self.gt.update()
        ptr = self.gt.find(*actions)
        
        # print(self.rp.SB2i.keys())
        myid = self.rp.h2i(myh, isBB)
        prob = ptr.actprob[:, myid]
        
        if debug:
            tmp = [c.signature for c in ptr.children]
            with np.printoptions(precision = 3, suppress = True):
                print(f"[DEBUG][postflop.act] choosing from {tmp} with p {prob}")
            if len(actions) > 0:
                print(f"[DEBUG] opp. range:")
                self.gt.find(*(actions[:-1])).show()
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
            if random() < BBp[i] + eps: BBr.append(x)
        return BBr
    
    def sample(self, p, BB = True, eps = 0.02, minSamples = 100):
        cnt, BBr, ieps = 0, self.sampleFrom(p, BB, eps), eps
        while cnt < 10 and len(BBr) < minSamples:
            cnt += 1
            p, ieps = p ** 0.8, ieps + 0.5 * eps
            BBr = self.sampleFrom(p, BB, eps)
        return BBr

    def ranges(self, myh, *actions, eps = 0.05, minSamples = 70):
        '''
        given an action line, output (could be a sample) of BBr, SBr
        '''
        actions = self.transform(actions, self.cur, self.pot)
        if self.debug: print(f"[DEBUG][postflop.ranges] actions = {actions}")
        BBp, SBp = self.gt.condprob(*actions)
        BBp, SBp = self.norm(BBp), self.norm(SBp)
        BBh, SBh = self.rp.nHands(BB = True), self.rp.nHands(BB = False)

        if self.debug:
            with np.printoptions(precision = 3, suppress = True):
                print(f"[DEBUG][postflop.ranges] BBp, SBp = \n{BBp}\n{SBp}")
    
        BBr, SBr = self.sample(BBp, True, eps, minSamples), self.sample(SBp, False, eps, minSamples)
        
        if self.debug: print(f"[DEBUG][postflop.ranges]: \nBBr = {Shower.hs2s(BBr)}\nSBr = {Shower.hs2s(SBr)}")
        return BBr, SBr

