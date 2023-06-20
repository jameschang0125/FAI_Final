import numpy as np

# dtype = 'float16'
# positive signature are reserved for raise
SIGGT = -1
class GameTree():
    def __init__(self, lr = 0.3, decay = 0.98, **kwargs):
        '''
        [IDEA] lower decay for deeper nodes
        '''
        self.rp = None #rp
        self.state = None #state
        self.isBB = False # True if BB is going to choose from actions
        self.lr, self.decay = lr, decay
        self.BBpaid, self.SBpaid, self.pot = 0, 0, 0
        self.term = False
        self.msg = ""
        self.train = True
        self.children = []
        self.signature = SIGGT
        self.mark = None # DEBUG purpose
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

    def CTsignature(self, suppress = True, eps = 0.1):
        ans = {}
        for i, c in enumerate(self.children):
            if (not suppress) or np.sum(self.actprob[i]) > eps:
                ans[c.signature] = c.CTsignature(suppress, eps)
        return ans

    def lock(self, depth = 1):
        self.train = False
        if depth > 1:
            for c in self.children:
                c.lock(depth - 1)
    
    def reset(self, lr = 0.3):
        self.lr = lr
        for c in self.children:
            c.reset(lr)

    def find(self, *signatures):
        if len(signatures) == 0: return self
        for c in self.children:
            if c.signature == signatures[0]:
                return c.find(*(signatures[1:]))
            elif signatures[0] == 1 and c.signature == SIGCALLIN:
                return c.find(*(signatures[1:]))
        return None

    def marked(self, marker = 0):
        self.mark = marker
        for c in self.children:
            c.marked(marker)

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

        # cannot find, when call is equiv allin


        # error
        poss = [c.signature for c in self.children]
        raise ValueError(f"couldn't find signatures {signatures} within {poss}!")

    def update(self, BBr, SBr):
        return self._update(BBr, SBr)

    def _update(self, BBr, SBr):
        '''
        update: actprob
        return: EV, (BBh, SBh) shaped ndarray
        
        for terminal nodes, just simply overwrite this function
        '''
        if self.isBB:
            condp = self.actprob * BBr
            tmp = np.array([c.update(condp[i], SBr) for i, c in enumerate(self.children)])
            v = np.sum(tmp, axis = 0)
            if self.train:
                tmp2 = np.sum(tmp, axis = 2) / self.actprob
                maxt = np.argmax(tmp2, axis = 0)
                self.actprob *= 1 - self.lr
                for i, t in enumerate(maxt):
                    self.actprob[t][i] += self.lr
        else:
            condp = self.actprob * SBr
            tmp = np.array([c.update(BBr, condp[i]) for i, c in enumerate(self.children)])
            v = np.sum(tmp, axis = 0)
            if self.train:
                tmp2 = np.sum(tmp, axis = 1) / self.actprob # DEBUG
                mint = np.argmin(tmp2, axis = 0)
                self.actprob *= 1 - self.lr
                for i, t in enumerate(mint):
                    self.actprob[t][i] += self.lr
        
        # DEBUG
        if self.mark is not None:
            marker = self.mark
            print("---")
            print(tmp2[:, marker])
            for i, c in enumerate(self.children):
                print(f"[SIG] {c.signature}")
                if self.isBB: 
                    tmp4 = tmp[i][marker] / (condp[i][marker] * SBr * self.rp.fq[marker])
                else: 
                    tmp4 = tmp[i][:, marker] / (condp[i][marker] * BBr * self.rp.fq[marker])
                with np.printoptions(precision = 3, suppress = True):
                    print(tmp4)
            
            '''
            if self.isBB:
                tmp = ((tmp2)[:, 100] / BBr[100]) / np.sum(self.rp.fq[100] * SBr)
                opp = SBr / np.sum(SBr) * 100
            else:
                tmp = ((tmp2)[:, 100] / SBr[100]) / np.sum(self.rp.fq[100] * BBr)
                opp = BBr / np.sum(BBr) * 100
            tmp3 = np.maximum(self.actprob[:, 100], 1e-3)

            with np.printoptions(precision = 0, suppress = True):
                print("\nopp =")
                print(opp)
            with np.printoptions(precision = 3, suppress = True):
                print(tmp / (np.max(tmp) if self.isBB else np.min(tmp)), tmp3)
            print(tmp)
            '''
        '''
        if self.mark:
            # print(tmp)
            print(v)
            with np.printoptions(precision = 3, suppress = True):
                print(condp)
                print(BBr)
                print(SBr)
                print(self.actprob)
                exit()
                # print((np.sum(tmp, axis = 2) / condp)[:, 40])
        '''

        self.lr *= self.decay
        return v            

    def getTree(self):
        '''
        returns a dictionary
        '''
        if self.term: return self.signature
        return (self.signature, tuple(c.getTree() for c in self.children))

    def show(self, msg = None, suppress = True, verbose = False, eps = 0.1):
        if not self.term:
            if msg is None: prefix = ""
            else: prefix = msg + " - "
            with np.printoptions(precision = 3, suppress = True):
                for i, c in enumerate(self.children):
                    if (not suppress) or np.sum(self.actprob[i]) > eps:
                        print(prefix + c.msg, self.actprob[i], sep = '\n')
            if verbose:
                for i, c in enumerate(self.children):
                    if (not suppress) or np.sum(self.actprob[i]) > eps:
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
        tmp = self._update(self.BBr, self.SBr)
        return np.sum(tmp)           

class InheritGT(GameTree):
    def __init__(self, gt, **kwargs):
        super().__init__(**kwargs)
        self.rp = gt.rp
        self.state = gt.state
        self.isBB = not gt.isBB
        self.BBh, self.SBh = gt.BBh, gt.SBh
        self.lr, self.decay = gt.lr, gt.decay
        self.BBpaid, self.SBpaid, self.pot = gt.BBpaid, gt.SBpaid, gt.pot

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
        
        # DEBUG
        self.WIN, self.LOSE = WIN, LOSE
    
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
                if not self.isBB: self.BBpaid = x + self.pot // 2
                else: self.SBpaid = x + self.pot // 2
            self._buildChild(ct)
    return _RAISE

CHECK = RAISE(x = 0, msg = "C")
LIMP = RAISE(x = 10, msg = "C")
ALLIN = RAISE(msg = "A") # signature 1

ALLINTREE = {
    ALLIN: {
        FOLD: None,
        CALLIN: None
    }
}

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
            self.pot = x
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
