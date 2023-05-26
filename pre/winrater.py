import pickle

from game.engine.hand_evaluator import HandEvaluator as HE
from pre.hand_processer import HandProcesser as HP
from tqdm import tqdm
import numpy as np
from itertools import product
from functools import partialmethod
from tqdm.contrib.concurrent import process_map

class winRater():
    def __init__(self):
        pass
    
    @classmethod
    def wr(self, xy, v = False, n = 10000, **kwargs):
        '''
        x, y: both (0 ~ 12, 0 ~ 12)
        v: verbose
        '''
        x, y = xy
        if x == y:
            return .5
        
        x, y = np.array(x) + 2, np.array(y) + 2
        ans = 0.
        iterator = tqdm(range(n)) if v else range(n)
        for t in iterator:
            ans += self.trial(x, y, **kwargs)
        return ans / n        
    
    @classmethod
    def trial(self, x, y, flop = 5):
        X, Y, Z = HP.genHand(*x), HP.genHand(*y), HP.genCards(flop)
        while HP.isConflict(X, Y, Z):
            X, Y, Z = HP.genHand(*x), HP.genHand(*y), HP.genCards(flop)
        
        xe, ye = HE.eval_hand(X, Z), HE.eval_hand(Y, Z)
        return 1. if xe > ye else (.5 if xe == ye else 0.)
    
    @classmethod
    def allWR(self, v = 1, dumppath = "pre/res/wr5.pickle", **kwargs):
        '''
        returns a (13 * 13) * (13 * 13) array of winrate
        '''

        ans = np.zeros((13, 13, 13, 13))

        iterator = product(range(13), range(13), range(13), range(13))
        if v == 1: iterator = tqdm(iterator, total = 13 ** 4)

        for xi, xj, yi, yj in iterator:
            ans[xi][xj][yi][yj] = self.wr(((xi, xj), (yi, yj)), v == 2, **kwargs)
        
        if dumppath is not None:
            with open(dumppath, 'wb') as f:
                pickle.dump(ans, f)

        return ans
    
    @classmethod
    def paraWR(self, v = 0, dumppath = "pre/res/wr5.pickle", workers = 70, **kwargs):
        '''
        same as allWR, but multiprocess
        [WARN] verbose settings has no effect on this
        '''

        ans = np.zeros((13, 13, 13, 13))

        work = []
        for xi, xj, yi, yj in product(range(13), range(13), range(13), range(13)):
            work.append(((xi, xj), (yi, yj)))

        singleWR = partialmethod(self.wr, v = v == 2, **kwargs).__get__(self)
        ret = process_map(singleWR, work, max_workers = workers)

        for i in range(len(work)):
            xi, xj = work[i][0]
            yi, yj = work[i][1]
            ans[xi][xj][yi][yj] = ret[i]

        if dumppath is not None:
            with open(dumppath, 'wb') as f:
                pickle.dump(ans, f)

        return ans