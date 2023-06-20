from src.pre.winrater import winRater as WR
from src.pre.range_preprocesser import RangePreProcesser as RPP
from src.eqcalc.test import testrs, testAoF
from src.pre.equitizer import Equitizer as EZ
from src.pre.equireader import Equireader as EQ
from src.pre.deepequitizer import DeepEquitizer as DEZ
from src.pre.test import testrp
from src.pre.test import testrs as testrs2
from src.pre.bestrsize import run

# WR.allWR()
# WR.paraWR(n = 100000, dumppath = "pre/res/wr5_100k.pickle")
# WR().dumpInfo()
# print(WR().wrTable[12][12]) # AA vs others

# RPP().gen()
# testrs()

# testAoF()

# EZ().gen()
# DEZ().gen()
#eq = EQ()
#for i in range(21):
#    print(f"{i} ::")
#    print(eq.showeq(i))

#testrp()
#testrs2()

run()
