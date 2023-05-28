class State():
    def __init__(self, my = 1000, isBB = False, turn = 19, equitizer = None):
        '''
        turn : turn left
        eqt.wr(chip, turn) returns the equity of BB
        '''
        self.my = my
        self.turn = turn
        self.eqt = equitizer
    
    def __wr(self, x):
        '''
        TODO: this is just a test function
        '''
        if self.my + x > 1000 + 7.5 * self.turn: return 1
        if self.my + x < 1000 - 7.5 * self.turn: return 0
        return 0.5 + 0.2 * (self.my + x - 1000) / (7.5 * self.turn)

    def wr(self, x):
        if self.eqt is None: return self.__wr(x)
        elif self.isBB: return self.eqt.wr(self.my + x, turn)
        else: return 1 - self.eqt.wr(2000 - self.my - x, turn)

    def to(self, my = 0):
        return State(self.my + my, equitizer = self.eqt)
