from multiplay import play, ais
from random import randint
from tqdm import tqdm
import sys

N = 200
win, lose, tie, error = [], [], [], []
for i in tqdm(range(N)):
    with open(f"tmp/log/{i}", "w") as sys.stdout:
        res = play(randint(0, len(ais) - 1), verbose = 1, debug = True)
        sys.stdout.flush()
    if res is None:
        error.append(i)
    elif res == 0:
        lose.append(i)
    elif res == 1:
        win.append(i)
    else:
        tie.append(i)

print(f"[WIN] {win}", file = sys.stderr)
print(f"[LOSE] {lose}", file = sys.stderr)
print(f"[TIE] {tie}", file = sys.stderr)
print(f"[ERR] {error}", file = sys.stderr)