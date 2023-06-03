import random

from game.engine.card import Card
from game.engine.deck import Deck
from game.engine.hand_evaluator import HandEvaluator

def gen_cards(cards_str):
    return [Card.from_str(s) for s in cards_str]

def estimate_winning_rate(nb_simulation, hole_card=None, p2_card=None, community_card=None):
    if not hole_card: pick_unused_card(2)
    win_count = sum([winning_simulation(hole_card, p2_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation

def estimate_not_losing_rate(nb_simulation, hole_card=None, p2_card=None, community_card=None):
    if not hole_card: pick_unused_card(2)
    win_count = sum([not_losing_simulation(hole_card, p2_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation

def winning_simulation(hole_card, p2_card, community_card):
    if not p2_card: p2_card = pick_unused_card(2, hole_card)
    if len(community_card) < 5:
      community_card = community_card + pick_unused_card(5 - len(community_card), hole_card + p2_card)
    return 1 if HandEvaluator.eval_hand(hole_card, community_card) > HandEvaluator.eval_hand(p2_card, community_card) else 0

def not_losing_simulation(hole_card, p2_card, community_card):
    if not p2_card: p2_card = pick_unused_card(2, hole_card)
    if len(community_card) < 5:
      community_card = community_card + pick_unused_card(5 - len(community_card), hole_card + p2_card)
    return 1 if HandEvaluator.eval_hand(hole_card, community_card) >= HandEvaluator.eval_hand(p2_card, community_card) else 0

def pick_unused_card(card_num, used_card):
    used = [card.to_id() for card in used_card]
    unused = [card_id for card_id in range(1, 53) if card_id not in used]
    choiced = random.sample(unused, card_num)
    return [Card.from_id(card_id) for card_id in choiced]