from tqdm import tqdm
import pickle
from pre.realtime_processer import RealtimeProcesser

class PostRangeProcesser(RealtimeProcesser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PreRangeProcesser():
    def __init__(self,
                frepath = "pre/res/ifr.pickle",
                h2ipath = "pre/res/h2i.pickle", 
                i2hpath = "pre/res/i2h.pickle", 
                wrtpath = "pre/res/idwr.pickle"):
        
        with open(frepath, 'rb') as f:
            self.fq = pickle.load(f)
        with open(h2ipath, 'rb') as f:
            self._h2i = pickle.load(f)
        with open(i2hpath, 'rb') as f:
            self._i2h = pickle.load(f)
        with open(wrtpath, 'rb') as f:
            self.wr = pickle.load(f)
        self.fw = self.wr * self.fq
    
    def nHands(self, BB = True):
        return 169
    
    def h2i(self, h, BB = True):
        x, y = h
        m, n = x[1] - 2, y[1] - 2
        m, n = max(m, n), min(m, n)
        if x[0] == y[0]: m, n = n, m
        id = m + n * 13
        return self._h2i[id]