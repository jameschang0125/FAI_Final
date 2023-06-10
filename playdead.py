from multiplay import play, ais
from random import randint
from tqdm import tqdm

N = 200
for i in tqdm(range(N)):
    play(randint(0, len(ais) - 1))