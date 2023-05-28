from pre.winrater import winRater as WR
from pre.range_preprocesser import RangePreProcesser as RPP
from eqcalc.test import testrs
from pre.equitizer import Equitizer as EQ

# WR.allWR()
# WR.paraWR(n = 100000, dumppath = "pre/res/wr5_100k.pickle")
# WR().dumpInfo()
# print(WR().wrTable[12][12]) # AA vs others

# RPP().gen()
# testrs()

EQ().gen()

