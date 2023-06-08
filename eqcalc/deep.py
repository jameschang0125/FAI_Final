import numpy as np

# dtype = 'float16'

class GameTree():
    def __init__(self, lr = 0.9, decay = 0.98, **kwargs):
        '''
        [IDEA] lower decay for deeper nodes
        '''
        self.rp = None #rp
        self.state = None #state
        self.isBB = False # True if BB is going to choose from actions
        self.lr, self.decay = lr, decay
        self.BBpaid, self.SBpaid = 0, 0
        self.term = False
        self.msg = ""
        # inherited class initialize, then construct child
        # print(f"[CONSTRUCTOR] {type(self)}")

    def _buildChild(self, constructorTree):
        self.BBh, self.SBh = self.rp.nHands(BB = True), self.rp.nHands(BB = False)
        self.children = []
        # print(f"[BUILDTREE] {constructorTree}")
        for c, v in constructorTree.items():
            if isinstance(c, type):
                self.children.append(c(self, v))
        nHands, nChild = (self.BBh if self.isBB else self.SBh), len(self.children)
        self.actprob = np.full((nChild, nHands), 1 / nChild)

    def update(self, BBr, SBr):
        '''
        update: actprob
        return: EV, (BBh, SBh) shaped ndarray
        
        for terminal nodes, just simply overwrite this function
        '''
        if self.isBB:
            condp = BBr * self.actprob
            tmp = np.array([c.update(condp[i], SBr) for i, c in enumerate(self.children)])
            v = np.sum(tmp, axis = 0)
            maxt = np.argmax(np.sum(tmp, axis = 2) / condp, axis = 0)
            self.actprob *= 1 - self.lr
            for i, t in enumerate(maxt):
                self.actprob[t][i] += self.lr
        else:
            condp = SBr * self.actprob
            tmp = np.array([c.update(BBr, condp[i]) for i, c in enumerate(self.children)])
            v = np.sum(tmp, axis = 0)
            mint = np.argmin(np.sum(tmp, axis = 1) / condp, axis = 0)
            self.actprob *= 1 - self.lr
            for i, t in enumerate(mint):
                self.actprob[t][i] += self.lr
        
        self.lr *= self.decay
        return v            

    def show(self, msg = None):
        if not self.term:
            if msg is None: prefix = ""
            else: prefix = msg + " - "
            with np.printoptions(precision = 3, suppress = True):
                for i, c in enumerate(self.children):
                    print(prefix + c.msg, self.actprob[i], sep = '\n')
            for c in self.children:
                c.show(prefix + c.msg)

class ROOT(GameTree):
    def __init__(self, rp, state, **kwargs):
        super().__init__(**kwargs)
        self.rp = rp
        self.state = state
        n, m = self.rp.nHands(BB = True), self.rp.nHands(BB = False)
        self.BBr, self.SBr = np.ones(n), np.ones(m)

    def update(self):
        '''
        update: actprob
        return: EV, (BBh, SBh) shaped ndarray
        
        for terminal nodes, just simply overwrite this function
        '''
        if self.isBB:
            condp = self.actprob
            tmp = np.array([c.update(condp[i], self.SBr) for i, c in enumerate(self.children)])
            maxt = np.argmax(np.sum(tmp, axis = 2) / condp, axis = 0)
            self.actprob *= 1 - self.lr
            for i, t in enumerate(maxt):
                self.actprob[t][i] += self.lr
        else:
            condp = self.actprob
            tmp = np.array([c.update(self.BBr, condp[i]) for i, c in enumerate(self.children)])
            mint = np.argmin(np.sum(tmp, axis = 1) / condp, axis = 0)
            self.actprob *= 1 - self.lr
            for i, t in enumerate(mint):
                self.actprob[t][i] += self.lr
        
        self.lr *= self.decay
        return np.sum(tmp)           

class InheritGT(GameTree):
    def __init__(self, gt, **kwargs):
        super().__init__(**kwargs)
        self.rp = gt.rp
        self.state = gt.state
        self.isBB = not gt.isBB
        self.BBh, self.SBh = gt.BBh, gt.SBh
        self.lr, self.decay = gt.lr, gt.decay
        self.BBpaid, self.SBpaid = gt.BBpaid, gt.SBpaid

# terminals
# CALL incl. terminal CHECKS
class CALLIN(InheritGT):
    def __init__(self, gt, ct = None, **kwargs):
        super().__init__(gt, **kwargs)
        self.term = True
        self.msg = "C"    
    
    def update(self, BBr, SBr):
        return np.outer(BBr, SBr) * self.rp.fw

class CALL(InheritGT):
    def __init__(self, gt, ct = None, **kwargs):
        super().__init__(gt, **kwargs)
        self.term = True
        self.msg = "C"
        if not self.isBB: self.BBpaid = self.SBpaid
        else: self.SBpaid = self.BBpaid

        WIN = self.state(self.SBpaid) * self.rp.fq * self.rp.wr
        LOSE = self.state(-self.BBpaid) * self.rp.fq * (1 - self.rp.wr)
        self.EV = WIN + LOSE
    
    def update(self, BBr, SBr):
        return np.outer(BBr, SBr) * self.EV

class FOLD(InheritGT):
    def __init__(self, gt, ct = None, **kwargs):
        super().__init__(gt, **kwargs)
        self.term = True
        self.msg = "F"
        if not self.isBB: self.EV = self.state(-self.BBpaid) * self.rp.fq
        else: self.EV = self.state(self.SBpaid) * self.rp.fq

    def update(self, BBr, SBr):
        return np.outer(BBr, SBr) * self.EV

# non-terminals
# alias, notice that the functionalities are almost the same
# we need to rewrite in order to have different hash
def RAISE(x = None, msg = "R"):
    class _RAISE(InheritGT):
        def __init__(self, gt, ct, **kwargs):
            super().__init__(gt, **kwargs)
            self.msg = msg
            if x is not None:
                if not self.isBB: self.BBpaid = x
                else: self.SBpaid = x
            self._buildChild(ct)
    return _RAISE

LIMP = RAISE(x = 10, msg = "C")
ALLIN = RAISE(msg = "A")

# constructors
class BLINDS(ROOT):
    def __init__(self, rp, state, ct, **kwargs):
        super().__init__(rp, state, **kwargs)
        self.BBpaid = 10
        self.SBpaid = 5
        self._buildChild(ct)

def POT(x = None):
    class _POT(ROOT):
        def __init__(self, rp, state, ct, **kwargs):
            super().__init__(rp, state, **kwargs)
            if x is not None:
                self.BBpaid = x / 2
                self.SBpaid = x / 2
            self._buildChild(ct)
    return _POT

'''
ex:
POT(40)(rp, curState, {
    CHECK(): {
        CALL: None,
        RAISE(30): {
            FOLD: None,
            CALL: None,
            ALLIN: {
                FOLD: None,
                CALLIN: None
            }
        }
    },
    RAISE(30): {
        FOLD: None,
        CALL: None,
        ALLIN: {
            FOLD: None,
            CALLIN: None
        }
    },
    ALLIN(): {
        FOLD: None,
        CALLIN: None
    }
})
'''
