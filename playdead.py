from multiplay import play, ais
from random import randint

N = 100
for i in range(N):
    try:
        play(randint(0, len(ais) - 1))
    except Exception as e:
        print(e)
        exit()