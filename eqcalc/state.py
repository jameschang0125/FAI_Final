class State():
    def __init__(self, my = 1000, isBB = False, turn = 19, equitizer = None):
        '''
        turn : turn left
        eqt.wr(chip, turn) returns the equity of BB
        '''
        self.my = int(my)
        self.turn = turn
        self.eqt = equitizer
        self.isBB = isBB
    
    def thre(self, BB = 2): # because this is for next round
        BB = int(BB)
        n, m = self.turn // 2, (self.turn - 1) // 2
        BBthre = n * 10 + m * 5
        SBthre = n * 5 + m * 10
        BBthre = max(0, BBthre - (1000 - self.my))
        SBthre = max(0, SBthre - (self.my - 1000))
        B2thre = min(BBthre, SBthre)
        return BBthre if BB == 1 else (SBthre if BB == 0 else B2thre)
    
    def othre(self, BB = 2):
        BB = int(BB)
        n, m = (self.turn + 1) // 2, self.turn // 2
        BBthre = n * 10 + m * 5
        SBthre = n * 5 + m * 10
        B2thre = max(0, min(BBthre - (1000 - self.my), SBthre - (self.my - 1000)))
        return BBthre if BB == 1 else (SBthre if BB == 0 else B2thre)

    def __wr(self, x):
        '''
        TODO: this is just a test function
        '''
        if self.my + x > 1000 + 7.5 * self.turn: return 1
        if self.my + x < 1000 - 7.5 * self.turn: return 0
        return 0.5 + 0.2 * (self.my + x - 1000) / (7.5 * self.turn)

    def wr(self, x):
        return self(x)
        '''
        if self.isBB:
            if self.eqt is None: return self.__wr(x)
            return self.eqt.wr(self.turn, self.my + x)
        else:
            if self.eqt is None: return 1 - self.__wr(-x)
            return 1 - self.eqt.wr(self.turn, 2000 - self.my - x)
        '''

    def __call__(self, x):
        return self.eqt.wr(self.turn, self.my + x) if self.isBB else 1 - self.eqt.wr(self.turn, 2000 - self.my - x)

    def to(self, my = 0):
        return State(self.my + my, not self.isBB, self.turn - 1, equitizer = self.eqt)
