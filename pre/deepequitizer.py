from eqcalc.state import State
from tqdm.contrib.concurrent import process_map
import pickle
import numpy as np
from functools import partialmethod
from eqcalc.deep import *
from subagent.heuristics import *
from subagent.newclass import PreRangeProcesser as PRP

class Equitizer():
    '''
    equity calculator
    '''
    size = 150
    offset = 850 # 1000 - size
    nHands = 13 * 13

    def __init__(self):
        self.eq = np.zeros((21, self.size * 2 + 1)) # turn left, BB.chips (BEFORE paying BB) - 860
        self.BBr = np.zeros((21, self.size * 2 + 1, self.nHands))
        self.SBr = np.zeros((21, self.size * 2 + 1, self.nHands))

    @classmethod
    def __thre(self, turn, isBB):
        x, y = turn // 2, (turn + 1) // 2
        if not isBB: x, y = y, x
        return x * 5 + y * 10

    def wr(self, turn, z):
        x = z - self.offset
        y = self.__win(turn, x)
        if y is not None: return y
        else:
            return self.eq[turn][int(x)]
    
    @classmethod
    def __win(self, turn, x):
        u, d = self.size + self.__thre(turn, True), self.size - self.__thre(turn, False)
        if x < d: return 0
        if x > u: return 1
        return None

    @classmethod
    def _iswin(self, turn, x):
        u, d = self.size + self.__thre(turn, True), self.size - self.__thre(turn, False)
        return self.__win(turn, x - self.offset)

    def _calc(self, turn, x):
        y = self.__win(turn, x)
        if y == 0: return y, None, None
        if y == 1: return y, None, None

        nIter, decay = 700, 0.99

        cur = State(BBchip, turn = turn, equitizer = self)
        gt = BLINDS(PRP(), cur, {
            FOLD: None,
            LIMP: {
                PRECALL: None,
                **{
                RAISE(i, msg = f"R({i})"): {
                    FOLD: None,
                    PRECALL: None,
                    **{
                    RAISE(int(i * j)):{
                        FOLD: None,
                        PRECALL: None,
                        ALLIN: {
                            FOLD: None,
                            CALLIN, None
                        }
                    } for j in [2.5, 3, 3.5, 4] },
                    ALLIN: {
                        FOLD: None,
                        CALLIN: None
                    }
                } for i in list(range(15, 25, 1)) + [30, 35, 40]},
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            },
            **{
            RAISE(i, msg = f"R({i})"): {
                FOLD: None,
                PRECALL: None,
                **{
                RAISE(int(i * j)):{
                    FOLD: None,
                    PRECALL: None,
                    ALLIN: {
                        FOLD: None,
                        CALLIN, None
                    }
                } for j in [2.5, 3, 3.5, 4]},
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            } for i in list(range(15, 25, 1)) + [30, 35, 40]},
            ALLIN: {
                FOLD: None,
                CALLIN: None
            }
        }, decay = decay)

        for i in range(nIter):
            v = gt.update()
        return v, gt

    def __gen(self, turn, workers = 70, **kwargs):
        '''
        Suppose (turn - 1) is calculated
        '''
        if turn == 0:
            self.eq[0][self.size] = 0.5
            for i in range(self.size + 1, self.size * 2 + 1):
                self.eq[0][i] = 1
            return

        ## TODO: thing below this is not done
        # accelerate for prevent repeat calc
        work = []
        for i in np.arange(self.size * 2 + 1):
            if i % 5 <= 1:
                work.append(i)

        calc = partialmethod(self._AoFcalc, turn).__get__(self)
        ret = process_map(calc, work, max_workers = workers, chunksize = 1)

        # print(ret[0])
        for i, x in enumerate(work):
            self.eq[turn][x], self.BBr[turn][x], self.SBr[turn][x] = ret[i]
            if x % 5 == 1:
                for y in range(x + 1, x + 4):
                    self.eq[turn][y], self.BBr[turn][y], self.SBr[turn][y] = ret[i]
