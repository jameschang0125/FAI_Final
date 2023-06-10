from eqcalc.deep import *
from itertools import product
from eqcalc.state import State
from pre.equireader import Equireader as EQ
from pre.range_processer import RangeProcesser as RP
from tqdm import tqdm

# hotfix
class RP2(RP):
    def __init__(self):
        super().__init__()
    
    def nHands(self, BB = True):
        return 169

def preflopNorm(rp, cur):
    return BLINDS(rp, cur, {
        FOLD: None,
        LIMP: {
            CALL: None,
            RAISE(25): {
                FOLD: None,
                CALL: None,
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            }
        },
        RAISE(25): {
            FOLD: None,
            CALL: None,
            ALLIN: {
                FOLD: None,
                CALLIN: None
            }
        },
        ALLIN: {
            FOLD: None,
            CALLIN: None
        }
    })

def preflopDeep(rp, cur):
    return BLINDS(rp, cur, {
        FOLD: None,
        LIMP: {
            CALL: None,
            **{
            RAISE(i, msg = f"R({i})"): {
                FOLD: None,
                CALL: None,
                ALLIN: {
                    FOLD: None,
                    CALLIN: None
                }
            } for i in range(15, 35)}
        },
        **{
        RAISE(i, msg = f"R({i})"): {
            FOLD: None,
            CALL: None,
            ALLIN: {
                FOLD: None,
                CALLIN: None
            }
        } for i in range(15, 35)},
        ALLIN: {
            FOLD: None,
            CALLIN: None
        }
    })

def testdeep():    
    rp = RP2()
    cur = State(1000, turn = 7, equitizer = EQ())

    gt = preflopDeep(rp, cur) # preflopNorm(rp, cur)
    ans = []
    for i in tqdm(range(1000)):
        tmp = gt.update()
        if i % 50 == 0: ans.append(tmp)

    with np.printoptions(precision = 3, suppress = True):
        print(np.array(ans))
    gt.show()

from subagent.preflop import preflopper
def testpreflopper():
    PRE = preflopper()
    myh = ((3, 14), (3, 12)) # AQs
    init = PRE.act(1000, 15, myh) # SB
    sseq = PRE.act(1000, 15, myh, init, 65, debug = True) # SB
    print(f"init: {init}, sseq: {sseq}")

def testspec():
    PRE = preflopper(debug = True)
    myh = ((3, 14), (3, 8)) # A8s
    print(f"[TEST] act 1")
    PRE.act(980, 18, myh)

    print(f"[TEST] act 2")
    PRE.act(980, 18, myh, 15, 103, nIter = 1) # create node

    #ptr = PRE.gt.find(15, 103)
    #ptr.mark = True
    PRE.act(980, 18, myh, 15, 103)


