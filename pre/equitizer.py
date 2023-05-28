from search import searcher as SS
from eqcalc.state import State
from tqdm.contrib.concurrent import process_map

class Equitizer():
    '''
    equity calculator
    '''
    def __init__(self):
        self.eq = np.zeros((20, 140 + 145 + 1)) # turn left, BB.chips (BEFORE paying BB) - 860
    
    @classmethod
    def __thre(self, turn, isBB):
        x, y = turn // 2 + (turn + 1) // 2
        if not isBB: x, y = y, x
        t = x * 5 + y * 10

    def query(self, turn, x):
        y = self.__win(x)
        if y is not None: return y
        else: return self.eq[turn][int(x)]
    
    @classmethod
    def __win(self, turn, x):
        u, d = self.__thre(turn, True), -self.__thre(turn, False)
        if x < d: return 0
        if x > u: return 1
        return None

    def _calc(self, turn, x):
        '''
        enumerate all possible raising set of SB

        TODO: maybe implement POSTFLOP sim ?
        '''
        y = self.__win(turn, x)
        if y is not None: return y

        ss = SS()
        state = State(860 + x - 10, True, turn - 1, self)
        u, d = self.__thre(turn, True), -self.__thre(turn, False)
        possibles = [10, np.arange(15, min(u, d)), 1000]
        
        v = 2
        for p in possibles:
            vh, a, c = ss.FR(p, state)
            if vh < v: v = vh

        return v

    def __gen(self, turn, workers = 70, **kwargs):
        '''
        Suppose (turn - 1) is calculated
        '''
        if turn == 0:
            self.eq[140] = 0.5

        work = np.arange(140 + 145 + 1)
        calc = partialmethod(self._calc, turn = turn).__get__(self)
        ret = process_map(calc, work, max_workers = workers, chunksize = 1)
        return np.array(ret)
    
    def gen(self, **kwargs):
        for i in range(20):
            print(f"[PROGRESS] equitizer.__gen({i})")
            self.__gen(i, **kwargs)
