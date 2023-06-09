from multiplay import play
from random import randint, ais

N = 100
for i in range(N):
    try:
        play(randint(0, len(ais) - 1), debug = True)
    except Exception as e:
        print(e)
        exit()