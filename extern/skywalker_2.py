from game.players import BasePokerPlayer
import random as rand
from utils import estimate_not_losing_rate, gen_cards
import pickle as pickle
import numpy as np
import math
from tqdm import tqdm

NB_SIMULATION = 2000

class AOFPlayer(BasePokerPlayer):
  def __init__(self):
    self.round_count = 0
    suit = ['C', 'D', 'H', 'S']
    rank = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    deck = [suit[i] + rank[j] for i in range(4) for j in range(13)]

    file = open('simulation2.pkl', 'rb')
    ests2d = pickle.load(file)
    file.close()

    # with tqdm(total=812175) as pbar:
    for a1 in range(52):
      for a2 in range(a1+1, 52):
        hole_card = [deck[a1], deck[a2]]
        for b1 in range(a1+1, 52):
          if b1 == a1 or b1 == a2:
            continue
          for b2 in range(b1+1, 52):
            if b2 == a1 or b2 == a2:
              continue
            p2_card = [deck[b1], deck[b2]]
            ests2d[tuple(p2_card)][tuple(hole_card)] = 1 - ests2d[tuple(hole_card)][tuple(p2_card)]
            # print(hole_card, p2_card, ests2d[tuple(p2_card)][tuple(hole_card)])
            #pbar.update(1)

    self.not_losing_rate = dict()
    # with tqdm(total=1624350) as pbar:
    for a1 in range(52):
      for a2 in range(a1+1, 52):
        hole_card = [deck[a1], deck[a2]]
        self.not_losing_rate[tuple(hole_card)] = 0
        cnt = 0
        for b1 in range(52):
          if b1 == a1 or b1 == a2:
            continue
          for b2 in range(b1+1, 52):
            if b2 == a1 or b2 == a2:
              continue
            p2_card = [deck[b1], deck[b2]]
            self.not_losing_rate[tuple(hole_card)] += ests2d[tuple(hole_card)][tuple(p2_card)]
            cnt += 1
            #pbar.update(1)
        self.not_losing_rate[tuple(hole_card)] /= cnt

    self.vals = np.array(list(self.not_losing_rate.values()))
    self.rate = [0.03, 0.033, 0.036, 0.046, 0.049, 0.055, 0.058, 0.067, 0.073, 0.092, 0.098, 0.107, 0.128, 0.15, 0.177, 0.22, 0.26, 0.37, 0.49, 1, 1]
    self.rate2 = [0.23, 0.233, 0.236, 0.246, 0.249, 0.255, 0.338, 0.367, 0.373, 0.392, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1]

  def declare_action(self, valid_actions, hole_card, round_state):
    self.pot = round_state['pot']['main']['amount']
    self.stack = round_state['seats'][round_state['next_player']]['stack']
    community_card = round_state['community_card']
    all_fold_threshold = 1000 + math.ceil((20 - self.round_count) / 2) * 10 + math.ceil((20 - self.round_count) / 2) * 5
    if len(community_card) == 0: # preflop
      print(hole_card)
      est = self.not_losing_rate[tuple(hole_card)] if tuple(hole_card) in self.not_losing_rate else self.not_losing_rate[tuple([hole_card[1], hole_card[0]])]
      print(est)
      if self.stack > all_fold_threshold:
        return "fold", 0
      elif est > np.percentile(self.vals, 100 * (1 - self.rate[self.round_count])):
        self.call_2_end = True
        if not valid_actions[2]["amount"]["max"] == -1:
          return "raise", max(min(150, valid_actions[2]["amount"]["max"]), valid_actions[2]["amount"]["min"])
        else:
          return "call", valid_actions[1]["amount"]
      elif self.call_2_end or valid_actions[1]["amount"] <= 20:
        return "call", valid_actions[1]["amount"]
      else:
        return "fold", 0
    else: # postflop
      est = estimate_not_losing_rate(nb_simulation=5000, hole_card=gen_cards(hole_card), community_card=gen_cards(community_card))
      print(est)
      mdv = valid_actions[1]["amount"] / (self.pot + valid_actions[1]["amount"])
      if est > 0.85 and self.call_2_end == True:
        return "call", valid_actions[1]["amount"]
      elif est > 0.85:
        self.call_2_end = True
        return "raise", max(min(150, valid_actions[2]["amount"]["max"]), valid_actions[2]["amount"]["min"])
      elif est > min(0.72, mdv) or valid_actions[1]["amount"] == 0 or self.call_2_end == True:
        return "call", valid_actions[1]["amount"]
      else:
        return "fold", 0

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.round_count = round_count
    self.call_2_end = False

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, new_action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass
    # print(round_state['seats'][0]['name'], round_state['seats'][0]['stack'])
    # print(round_state['seats'][1]['name'], round_state['seats'][1]['stack'])


def setup_ai():
  return AOFPlayer()
