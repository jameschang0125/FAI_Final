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
from subagent.postflop import postflopper
def testpreflopper():
    PRE = preflopper()
    myh = ((3, 14), (3, 12)) # AQs
    init = PRE.act(1000, 15, myh) # SB
    sseq = PRE.act(1000, 15, myh, init, 65, debug = True) # SB
    print(f"init: {init}, sseq: {sseq}")

def testspec():
    PRE = preflopper(debug = True)
    myh = ((3, 11), (3, 8)) # J8s
    print(f"[TEST] act 1")
    #PRE.act(1035, 6, myh, nIter = 1)
    #PRE.gt.mark = True
    PRE.act(1010, 1, myh, 30)

    '''
    print(f"[TEST] act 2")
    POST = postflopper(BBr, SBr, [(2, 6), (3, 14), (0, 8)], SBincl = myh, debug = False)
    POST.act(975, 8, myh, 20, street = 1)
    BBr, SBr = POST.ranges(myh, 20, -3)

    POST = postflopper(BBr, SBr, [(2, 6), (3, 14), (0, 8), (0, 8)], SBincl = myh, debug = True)
    POST.act(975, 8, myh, 60, street = 1)
    '''
    #PRE.act(1112, 15, myh, 10, 65)
    # PRE.act(1010, 3, myh, 15)
    # PRE.gt.find(15, 60).mark = True
    # PRE.act(960, 18, myh, 15, 60)

    '''
    print(f"[TEST] act 2")
    PRE.act(980, 18, myh, 15, 103, nIter = 1) # create node
    ptr = PRE.gt.find(15, 103)
    ptr.mark = True
    PRE.act(980, 18, myh, 15, 103)
    '''


