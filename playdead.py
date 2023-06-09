from multiplay import play, ais
from random import randint
from tqdm import tqdm

N = 200
for i in tqdm(range(N)):
    try:
        play(randint(0, len(ais) - 1))
    except Exception as e:
        print(e)
        exit()