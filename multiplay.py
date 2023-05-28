from tqdm.contrib.concurrent import process_map  # or thread_map
import time

import json
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai
from agents.my_player import setup_ai as my_ai

import numpy as np
# from baseline0 import setup_ai as baseline0_ai


def play(id):
    config = setup_config(max_round = 20, initial_stack = 1000, small_blind_amount = 5)
    config.register_player(name = "p1", algorithm = my_ai())
    config.register_player(name = "p2", algorithm = call_ai())
    res = start_poker(config, verbose = 0)
    x, y = res["players"][0]["stack"], res["players"][1]["stack"]
    if x > y: return 1
    if x < y: return 0
    return 0.5

if __name__ == '__main__':
    N = 100
    r = process_map(play, range(N), max_workers = 20)
    print(f"p1 winrate = {np.sum(r) / N}")
