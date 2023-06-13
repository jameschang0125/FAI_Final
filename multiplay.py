from tqdm.contrib.concurrent import process_map  # or thread_map
import time
import sys

import json
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai
from agents.my_player import setup_ai as my_ai
from agents.my_player import quiet_ai, test_ai
from random import random
from agents.deep_player import setup_ai as deep_ai

# from extern.skywalker_2 import setup_ai as casper_ai
import numpy as np

from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai

import traceback

# ais = [baseline0_ai, baseline1_ai, baseline2_ai, baseline3_ai, baseline4_ai, baseline5_ai, my_ai, call_ai, random_ai]
ais = [baseline5_ai]

def play(id, verbose = 0, **kwargs):
    try:
        config = setup_config(max_round = 20, initial_stack = 1000, small_blind_amount = 5)
        my = deep_ai(**kwargs)
        if random() < 0.5:
            config.register_player(name = "me", algorithm = my)
            config.register_player(name = "opp", algorithm = ais[id]())
            switched = False
        else:
            config.register_player(name = "opp", algorithm = ais[id]())
            config.register_player(name = "me", algorithm = my)
            switched = True

        res = start_poker(config, verbose = verbose)

        for d in res["players"]:
            if d["name"] == "me":
                x = d["stack"]
            else:
                y = d["stack"]
        
        tmp = 1 if x > y else (0 if x < y else 0.5)
        return 1 - tmp if switched else tmp
    except Exception as e:
        print(f"[SWITCH = {switched}][#{id}] {repr(e)}")
        traceback.print_exc()
        return None

if __name__ == '__main__':
    N = 1000
    for a in range(len(ais)):
        print(f"vs baseline {a} ::")
        r = process_map(play, [a for _ in range(N)], max_workers = 40, chunksize = 1)
        
        errcnt, errs, cnt, wins = 0, [], 0, 0
        for i, v in enumerate(r):
            if v is None:
                errs.append(i)
                errcnt += 1
            else:
                wins += i
                cnt += 1

        p = wins / cnt
        stderr = (p * (1 - p) / cnt) ** 0.5
        print(f"[RESULT] winrate = {'%.4f'%p} ± {'%.4f'%(stderr * 1.96)}, errrate = {'%.4f'%(errcnt/N)}")
        print(f"[ERROR LIST] {errs}")
