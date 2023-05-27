class State():
    def __init__(self, my = 1000, isBB = False, turn = 19):
        '''
        turn : turn left
        '''
        self.my = my
        self.turn = turn
    
    def wr(self, x):
        '''
        TODO: this is just a test, use dp to calculate exact
        '''
        if self.my + x > 1000 + 7.5 * self.turn: return 1
        if self.my + x < 1000 - 7.5 * self.turn: return 0
        return 0.5 + 0.2 * (self.my + x - 1000) / (7.5 * self.turn)

    def to(self, my = 0, turn = 0):
        return State(self.my + my, self.turn + turn)
