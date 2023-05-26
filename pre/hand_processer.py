from game.engine.hand_evaluator import HandEvaluator as HE
from game.engine.card import Card
from numpy.random import choice, randint
import numpy as np

class HandProcesser():
    def __init__(self):
        pass
    
    @classmethod
    def genHand(self, x, y):
        if x >= y: # XYo or XX
            a, b = choice(np.arange(4), 2)
            return [Card(a, x), Card(b, y)]
        if x < y: # XYs
            a = randint(4)
            return [Card(a, x), Card(a, y)]
    
    @classmethod
    def isConflict(self, *x):
        '''
        x: list of (Card, Card)
        '''
        tmp = []
        for cardList in x:
            tmp += cardList
        tmp = [(c.suit, c.rank) for c in tmp]
        return len(set(tmp)) < len(tmp)
    
    @classmethod
    def genCards(self, n = 1):
        return [Card(randint(4), randint(2, 15)) for _ in range(n)]

