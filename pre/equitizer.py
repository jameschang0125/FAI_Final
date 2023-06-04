from eqcalc.search import searcher as SS
from eqcalc.state import State
from tqdm.contrib.concurrent import process_map
import pickle
import numpy as np
from functools import partialmethod

class Equitizer():
    '''
    equity calculator
    '''
    size = 150
    offset = 850 # 1000 - size
    nHands = 13 * 13

    def __init__(self):
        self.eq = np.zeros((20, self.size * 2 + 1)) # turn left, BB.chips (BEFORE paying BB) - 860
        self.BBr = np.zeros((20, self.size * 2 + 1, self.nHands))
        self.SBr = np.zeros((20, self.size * 2 + 1, self.nHands))

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
        '''
        enumerate all possible raising set of SB

        TODO: maybe implement POSTFLOP sim ?
        '''
        y = self.__win(turn, x)
        if y is not None: return y

        ss = SS()
        state = State(self.offset + x - 10, True, turn - 1, self)
        u, d = self.__thre(turn, True), -self.__thre(turn, False)
        possibles = [10, 1000] # [10, 1000] + np.arange(15, min(u, d)).tolist()
        
        v = 2
        for p in possibles:
            vh, a, c = ss.FR(p, state)
            if vh < v: v = vh

        return v

    def _AoFcalc(self, turn, x):
        y = self.__win(turn, x)
        if y == 0: return y, np.ones(self.nHands), np.zeros(self.nHands)
        if y == 1: return y, np.zeros(self.nHands), np.ones(self.nHands)

        ss = SS()
        state = State(self.offset + x - 10, False, turn - 1, self)
        v, myr, oppr = ss.AoF(state)
        return v, myr, oppr


    def __gen(self, turn, workers = 70, **kwargs):
        '''
        Suppose (turn - 1) is calculated
        '''
        if turn == 0:
            self.eq[0][self.size] = 0.5
            for i in range(self.size + 1, self.size * 2 + 1):
                self.eq[0][i] = 1
            return

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

    
    def gen(self, eqpath = "pre/res/AoFeq.pickle"
                , BBpath = "pre/res/AoFBBr.pickle"
                , SBpath = "pre/res/AoFSBr.pickle"
                , **kwargs):
        for i in range(20):
            print(f"[PROGRESS] equitizer.__gen({i})")
            self.__gen(i, **kwargs)

        if eqpath is not None:
            with open(eqpath, 'wb') as f:
                pickle.dump(self.eq, f)

        if BBpath is not None:
            with open(BBpath, 'wb') as f:
                pickle.dump(self.BBr, f)

        if SBpath is not None:
            with open(SBpath, 'wb') as f:
                pickle.dump(self.SBr, f)

        # DEBUG
        s = self.size - 10
        for i in range(20):
            print(f"turn{i} :: \neq: {self.eq[i]}\nBBr:{self.BBr[i][s]}\nSBr:{self.SBr[i][s]}")
        