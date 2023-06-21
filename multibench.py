from tqdm.contrib.concurrent import process_map
import numpy as np
from random import random

from game.game import setup_config, start_poker

from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai
from src.agents.deep_player     import setup_ai as deep_ai
from src.agents.my_player       import setup_ai as aof_ai
from src.agents.finale_player   import setup_ai as final_ai

ais = [baseline0_ai, baseline1_ai, baseline2_ai, baseline3_ai, baseline4_ai, baseline5_ai, aof_ai, deep_ai]
ais = [aof_ai]
tester_ai = final_ai

def play1(id):
    try:
        x, y = tester_ai(), ais[id]()
        config = setup_config(max_round = 20, initial_stack = 1000, small_blind_amount = 5)
        if random() < 0.5:
            config.register_player(name = "me", algorithm = x)
            config.register_player(name = "opp", algorithm = y)
            switched = False
        else:
            config.register_player(name = "opp", algorithm = y)
            config.register_player(name = "me", algorithm = x)
            switched = True
        
        res = start_poker(config, verbose = 0)
        for d in res["players"]:
            if d["name"] == "me": a = d["stack"]
            else: b = d["stack"]
        ans = 1 if a > b else (0 if a < b else 0.5)
        return ans, x.decTime, x.recTime
    except :
        return None

def tops(x):
    return np.array([x.max(axis = 1), np.percentile(x, 99, axis = 1), np.percentile(x, 90, axis = 1)])

def play(id, num):
    print(f"vs baseline {id} ::")
    r = process_map(play1, [id for _ in range(num)], max_workers = 20, chunksize = 1)

    wins, errcnt, decTimes, recTimes = 0, 0, np.zeros((4, num)), np.zeros((4, num))
    for i, x in enumerate(r):
        if x is None:
            errcnt += 1
            continue
        ans, decTime, recTime = x
        decTimes[:, i], recTimes[:, i] = decTime, recTime
        wins += ans
    
    cnt, p = num - errcnt, wins / (num - errcnt)
    stderr = (p * (1 - p) / (cnt - 1)) ** 0.5
    print(f"[RESULT] winrate = {'%.4f'%p} ± {'%.4f'%(stderr * 1.96)}, errrate = {'%.4f'%(errcnt / num)}")
    print(f"[TIMING] declare action: (street) * (max, top 0.01, top 0.1)")
    with np.printoptions(precision = 3, suppress = True):
        print(tops(decTimes))
    print(f"[TIMING] receive street: (street) * (max, top 0.01, top 0.1)")
    with np.printoptions(precision = 3, suppress = True):
        print(tops(recTimes))

if __name__ == '__main__':
    for i in range(len(ais)):
        play(i, 400)
