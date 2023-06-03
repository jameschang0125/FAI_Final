import numpy as np
import pickle
from pre.winrater import winRater as WR
from tqdm import tqdm
from itertools import product
from functools import partialmethod

from pre.range_processer import RangeProcesser
from game.engine.hand_evaluator import HandEvaluator as HE
from game.engine.card import Card

from random import shuffle, sample

class RealtimeProcesser(RangeProcesser):
    def __init__(self, BBr, SBr, comm, BBincl = None, SBincl = None, rsSize = 50, csSize = 50):
        '''
        BBr & SBr : collection of (c, c)
        c : (suit, rank)
        '''
        super().__init__(boot = False)
        possibles = self.drawcomm(comm, csSize)
        bbh, sbh = min(len(BBr), rsSize), min(len(SBr), rsSize)
        BBr = sample(BBr, bbh)
        SBr = sample(SBr, sbh)
        if BBincl and BBincl not in BBr: BBr[-1] = BBincl
        if SBincl and SBincl not in SBr: SBr[-1] = SBincl

        self.BBr, self.SBr = [tuple(t) for t in BBr], [tuple(t) for t in SBr]
        wrt = self.gen(BBr, SBr, possibles)
        fqt = self.genf(BBr, SBr)
        self.cvt(wrt, fqt)
        
        self.fwSum = self._2dsum(self.fw)
        self.wrSum = self._2dsum(self.wr)
        self.fqSum = self._2dsum(self.fq)

        # DEBUG
        # print(self.fw)
        # print(wrt)

    def i2h(self, i, BB = True):
        return self.BBr[self.BB_i2h[i]] if BB else self.SBr[self.SB_i2h[i]]
    
    def is2h(self, i, BB = True):
        return [self.i2h(j, BB) for j in i]

    def h2i(self, h, BB = True):
        return self.BB2i[h] if BB else self.SB2i[h]

    @classmethod
    def hs2s(self, hs):
        return [self.h2s(h) for h in hs]

    @classmethod
    def h2s(self, x):
        return self.c2s(x[0]) + self.c2s(x[1])
        
    @classmethod
    def c2s(self, c):
        s, r = c
        return "23456789TJQKA"[r - 2] + "cdhs"[s]

    def cvt(self, wrt, fqt):
        '''
        copy from range preprocesser
        order hand by wr
        # TODO: not sort by overall wr
        '''
        fw = wrt * fqt
        m, n = fw.shape
        BBwr, SBwr = self.wr(fw, fqt), self.wr(fw, fqt, False)

        self.BB_i2h = np.flip(np.argsort(BBwr))
        self.SB_i2h = np.flip(np.argsort(SBwr))
        self.BB_h2i, self.SB_h2i = np.zeros(m, dtype = 'int16'), np.zeros(n, dtype = 'int16')
        self.BB_h2i[self.BB_i2h] = np.arange(m)
        self.SB_h2i[self.SB_i2h] = np.arange(n)

        self.BB2i = {b : self.BB_h2i[i] for i, b in enumerate(self.BBr)}
        self.SB2i = {b : self.SB_h2i[i] for i, b in enumerate(self.SBr)}

        wrt2, fqt2 = np.zeros((m, n)), np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                wrt2[i][j] = wrt[self.BB_i2h[i]][self.SB_i2h[j]]
                fqt2[i][j] = fqt[self.BB_i2h[i]][self.SB_i2h[j]]
        fqt2 /= np.sum(fqt2)

        self.wr, self.fq, self.fw = wrt2, fqt2, wrt2 * fqt2

    def wr(self, fw, fq, BB = True):
        m, n = fw.shape
        if BB:
            return np.array([np.sum(fw[i]) / np.sum(fq[i]) for i in range(m)])
        fw, fq = np.swapaxes(fw, 0, 1), np.swapaxes(fq, 0, 1) 
        return np.array([1 - np.sum(fw[i]) / np.sum(fq[i]) for i in range(n)])

    def nHands(self, BB):
        return self.fw.shape[0] if BB else self.fw.shape[1]

    @classmethod
    def genf(self, BBr, SBr):
        m, n = (len(BBr), len(SBr))
        ans = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                bb, sb = BBr[i], SBr[j]
                ans[i][j] = 1 if len(set(list(bb) + list(sb))) == 4 else 0
        return ans
    
    @classmethod
    def gen(self, BBr, SBr, comms):
        m, n = (len(BBr), len(SBr))
        ans = np.zeros((m, n))
        for comm in comms:
            ans += self.genwrTable(BBr, SBr, comm)
        ans /= len(comms)
        return ans

    @classmethod
    def genwrTable(self, BBr, SBr, comm):
        bbs, sbs = self.solvecomm(BBr, SBr, comm)
        m, n = (len(BBr), len(SBr))
        ans = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                xe, ye = bbs[i], sbs[j]
                ans[i][j] = 1. if xe > ye else (.5 if xe == ye else 0.)
        return ans

    @classmethod
    def solvecomm(self, BBr, SBr, comm):
        '''
        ret: [strengths], [strengths]
        '''
        return [self.eval(list(h), comm) for h in BBr], [self.eval(h, comm) for h in SBr]
    
    @classmethod
    def eval(self, x, y):
        return HE.eval_hand([Card(2 << i[0], i[1]) for i in x], [Card(2 << i[0], i[1]) for i in y])


    def drawcomm(self, comm, lim):
        if len(comm) == 5:
            return [comm]
        
        s = set(comm)
        oldp = [(i, j) for i, j in product(range(4), range(2, 15))]
        p = []
        for c in oldp:
            if c not in s: p.append(c)

        if len(comm) == 4:
            ans = [comm + [c] for c in p]
            shuffle(ans)
        
        else: # len(comm) == 3
            newp = []
            for i in range(len(p)):
                for j in range(i):
                    newp.append(comm + [p[i], p[j]])
            ans = [comm + [c] for c in p]
            shuffle(ans)
            
        return ans[:min(lim, len(ans))]

        


