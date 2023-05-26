from game.engine.hand_evaluator import HandEvaluator as HE
from game.engine.card import Card

p1, p2 = ["S3", "S5"], ["S2", "S7"]
comm = ["D6", "D8", "D9", "CJ", "CA"]

p1 = [Card.from_str(c) for c in p1]
p2 = [Card.from_str(c) for c in p2]
comm = [Card.from_str(c) for c in comm]

print(f"{HE.eval_hand(p1, comm):b}")
print(f"{HE.eval_hand(p2, comm):b}")

