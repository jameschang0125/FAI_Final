import numpy as np

# dtype = 'float16'
# positive signature are reserved for raise
SIGGT = -1
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
        self.train = True
        self.children = []
        self.signature = SIGGT
        # inherited class initialize, then construct child
        # print(f"[CONSTRUCTOR] {type(self)}")

    def _buildChild(self, constructorTree):
        self.BBh, self.SBh = self.rp.nHands(BB = True), self.rp.nHands(BB = False)
        # print(f"[BUILDTREE] {constructorTree}")
        for c, v in constructorTree.items():
            if isinstance(c, type):
                self.children.append(c(self, v))
        nHands, nChild = (self.BBh if self.isBB else self.SBh), len(self.children)
        self.actprob = np.full((nChild, nHands), 1 / nChild)

    def addChild(self, constructorTree):
        # also resets the weights
        for c, v in constructorTree.items():
            self.children.append(c(self, v))
        nHands, nChild = (self.BBh if self.isBB else self.SBh), len(self.children)
        self.actprob = np.full((nChild, nHands), 1 / nChild)

    def lock(self, depth = 1):
        self.train = False
        if depth > 1:
            for c in self.children:
                c.lock(depth - 1)
    
    def reset(self, lr = 0.9):
        self.lr = lr
        for c in self.children:
            c.reset(lr)

    def find(self, *signatures):
        if len(signatures) == 0: return self
        for c in self.children:
            if c.signature == signatures[0]:
                return c.find(*(signatures[1:]))
        return None

    def condprob(self, *signatures):
        if len(signatures) == 0: 
            BBh, SBh = self.rp.nHands(BB = True), self.rp.nHands(BB = False)
            return np.ones(BBh), np.ones(SBh)

        # DEBUG
        poss = [c.signature for c in self.children]
        # print(f"[DEBUG][deep.condprob] poss = {poss}")

        for i, c in enumerate(self.children):
            if c.signature == signatures[0]:
                BBr, SBr = c.condprob(*(signatures[1:]))
                if self.isBB:
                    return BBr * self.actprob[i], SBr
                else:
                    return BBr, SBr * self.actprob[i]
        
        # error
        poss = [c.signature for c in self.children]
        raise ValueError(f"couldn't find signatures {signatures} within {poss}!")

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
            if self.train:
                maxt = np.argmax(np.sum(tmp, axis = 2) / condp, axis = 0)
                self.actprob *= 1 - self.lr
                for i, t in enumerate(maxt):
                    self.actprob[t][i] += self.lr
        else:
            condp = SBr * self.actprob
            tmp = np.array([c.update(BBr, condp[i]) for i, c in enumerate(self.children)])
            v = np.sum(tmp, axis = 0)
            if self.train:
                mint = np.argmin(np.sum(tmp, axis = 1) / condp, axis = 0)
                self.actprob *= 1 - self.lr
                for i, t in enumerate(mint):
                    self.actprob[t][i] += self.lr
        
        self.lr *= self.decay
        return v            

    def getTree(self):
        '''
        returns a dictionary
        '''
        if self.term: return self.signature
        return (self.signature, tuple(c.getTree() for c in self.children))

    def show(self, msg = None, suppress = True):
        eps = 1e-3
        if not self.term:
            if msg is None: prefix = ""
            else: prefix = msg + " - "
            with np.printoptions(precision = 3, suppress = True):
                for i, c in enumerate(self.children):
                    if suppress and np.sum(self.actprob[i]) > eps:
                        print(prefix + c.msg, self.actprob[i], sep = '\n')
            for c in self.children:
                if suppress and np.sum(self.actprob[i]) > eps:
                    c.show(prefix + c.msg)

SIGROOT = -1
class ROOT(GameTree):
    def __init__(self, rp, state, **kwargs):
        super().__init__(**kwargs)
        self.rp = rp
        self.state = state
        self.signature = 0
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
SIGCALLIN = -2
class CALLIN(InheritGT):
    def __init__(self, gt, ct = None, **kwargs):
        super().__init__(gt, **kwargs)
        self.term = True
        self.msg = "C"
        self.signature = SIGCALLIN
    
    def update(self, BBr, SBr):
        return np.outer(BBr, SBr) * self.rp.fw

SIGCALL = -3
class CALL(InheritGT):
    def __init__(self, gt, ct = None, **kwargs):
        super().__init__(gt, **kwargs)
        self.term = True
        self.msg = "C"
        self.signature = SIGCALL
        if not self.isBB: self.BBpaid = self.SBpaid
        else: self.SBpaid = self.BBpaid

        WIN = self.state(self.SBpaid) * self.rp.fq * self.rp.wr
        LOSE = self.state(-self.BBpaid) * self.rp.fq * (1 - self.rp.wr)
        self.EV = WIN + LOSE
    
    def update(self, BBr, SBr):
        return np.outer(BBr, SBr) * self.EV

SIGFOLD = -4
class FOLD(InheritGT):
    def __init__(self, gt, ct = None, **kwargs):
        super().__init__(gt, **kwargs)
        self.term = True
        self.msg = "F"
        self.signature = SIGFOLD
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
            self.signature = 1 if x is None else x
            if x is not None:
                if not self.isBB: self.BBpaid = x
                else: self.SBpaid = x
            self._buildChild(ct)
    return _RAISE

CHECK = RAISE(x = 0, msg = "C")
LIMP = RAISE(x = 10, msg = "C")
ALLIN = RAISE(msg = "A") # signature 1

# constructors
class BLINDS(ROOT):
    def __init__(self, rp, state, ct, **kwargs):
        super().__init__(rp, state, **kwargs)
        self.BBpaid = 10
        self.SBpaid = 5
        self._buildChild(ct)

def POT(x = None, y = None):
    class _POT(ROOT):
        def __init__(self, rp, state, ct, **kwargs):
            super().__init__(rp, state, **kwargs)
            if x is not None:
                if y is None:
                    self.BBpaid = x / 2
                    self.SBpaid = x / 2
                else:
                    self.BBpaid, self.SBpaid = x, y
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
