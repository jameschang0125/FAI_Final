from pre.realtime_processer import RealtimeProcesser as RP

from itertools import product

def testrp():
    pos = [(i, j) for i, j in product(range(4), range(2, 15))]
    BBr = []
    for i in range(len(pos)):
        for j in range(i):
            BBr.append((pos[i], pos[j]))
    SBr = BBr
    comm = [(3, 13), (0, 14), (2, 5)]
    r = RP(BBr, SBr, comm)

