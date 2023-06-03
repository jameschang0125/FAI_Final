from pre.winrater import winRater as WR
from pre.range_preprocesser import RangePreProcesser as RPP
from eqcalc.test import testrs, testAoF
from pre.equitizer import Equitizer as EZ
from pre.equireader import Equireader as EQ
from pre.test import testrp
from pre.test import testrs as testrs2

# WR.allWR()
# WR.paraWR(n = 100000, dumppath = "pre/res/wr5_100k.pickle")
# WR().dumpInfo()
# print(WR().wrTable[12][12]) # AA vs others

# RPP().gen()
# testrs()

# testAoF()

# EZ().gen()
#eq = EQ()
#for i in range(850, 1150, 10):
#    print(f"wr({i}): {eq.wr(18, i)}")

#testrp()
testrs2()
