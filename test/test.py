from game.engine.hand_evaluator import HandEvaluator as HE
from game.engine.card import Card

def test():
    p1, p2 = ["SA", "D6"], ["S2", "D7"]
    comm = ["C6", "D8", "D9", "DJ", "DA"]

    p1 = [Card.from_str(c) for c in p1]
    p2 = [Card.from_str(c) for c in p2]
    comm = [Card.from_str(c) for c in comm]

    print(f"{HE.eval_hand(p1, comm):b}")
    print(f"{HE.eval_hand(p2, comm):b}")

