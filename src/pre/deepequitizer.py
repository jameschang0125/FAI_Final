from src.eqcalc.state import State
from tqdm.contrib.concurrent import process_map
import pickle
import numpy as np
from functools import partialmethod
from src.eqcalc.deep import *
from src.subagent.heuristics import *
from src.subagent.newclass import PreRangeProcesser as PRP
import sys

class DeepEquitizer():
    '''
    equity calculator
    '''
    size = 150
    offset = 850 # 1000 - size
    nHands = 13 * 13

    def __init__(self):
        self.eq = np.zeros((21, self.size * 2 + 1)) # turn left, BB.chips (BEFORE paying BB) - 860
        self.gto = [None for _ in range(21)]

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
        return self.__win(turn, x - self.offset)

    def _calc(self, turn, x):
        y = self.__win(turn, x)
        if y == 0: return y, None
        if y == 1: return y, None

        nIter, decay = 700, 0.99

        cur = State(x + self.offset, turn = turn, equitizer = self).to()
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
                            CALLIN: None
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
                        CALLIN: None
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

        return v, gt.CTsignature()

    def __gen(self, turn, workers = 40, **kwargs):
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
        work = np.arange(self.size * 2 + 1).tolist()

        calc = partialmethod(self._calc, turn).__get__(self)
        ret = process_map(calc, work, max_workers = workers, chunksize = 1)

        self.gto[turn] = [r[1] for r in ret]
        self.eq[turn] = [r[0] for r in ret]

    def gen(self, eqpath = "src/pre/res/Deepeq.pickle"
                , gtpath = "src/pre/res/gto.pickle"
                , **kwargs):
        for i in range(21):
            print(f"[PROGRESS] equitizer.__gen({i})")
            self.__gen(i, **kwargs)
            with np.printoptions(precision = 4, suppress = True):
                print(self.eq[i])

        if eqpath is not None:
            with open(eqpath, 'wb') as f:
                pickle.dump(self.eq, f)

        if gtpath is not None:
            with open(gtpath, 'wb') as f:
                pickle.dump(self.gto, f)
        

