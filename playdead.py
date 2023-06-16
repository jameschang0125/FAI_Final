from multiplay import play, ais
from random import randint
from tqdm import tqdm
import sys
import traceback

N = 200
win, lose, tie, error = [], [], [], []
try:
    for i in range(N):
        print(f"[ITER] {i} ::", file = sys.stderr)
        with open(f"tmp/log/{i}", "w") as sys.stdout:
            res = play(randint(0, len(ais) - 1), verbose = 1, debug = True, pe = True)
            sys.stdout.flush()
        if res is None:
            error.append(i)
        elif res == 0:
            lose.append(i)
        elif res == 1:
            win.append(i)
        else:
            tie.append(i)
except KeyboardInterrupt:
    with open("tmp/deadout.txt", "w") as f:
        print(f"[WIN] {win}", file = f)
        print(f"[LOSE] {lose}", file = f)
        print(f"[TIE] {tie}", file = f)
        print(f"[ERR] {error}", file = f)
except Exception as e:
    with open("tmp/deadout.txt", "w") as f:
        print(f"[WIN] {win}", file = f)
        print(f"[LOSE] {lose}", file = f)
        print(f"[TIE] {tie}", file = f)
        print(f"[ERR] {error}", file = f)
        traceback.print_exc(file = f)


