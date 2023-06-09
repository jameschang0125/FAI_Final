class Shower():
    @classmethod
    def c2s(self, c):
        x, y = c
        return "0123456789TJQKA"[y] + "cdhs"[x]

    @classmethod
    def h2s(self, h):
        return self.c2s(h[0]) + self.c2s(h[1])
        
    @classmethod
    def hs2s(self, hs):
        return [self.h2s(h) for h in hs]
    
    @classmethod
    def show(self, hs):
        if isinstance(hs, list) or isinstance(hs, tuple):
            print(self.hs2s(hs))
        raise ValueError