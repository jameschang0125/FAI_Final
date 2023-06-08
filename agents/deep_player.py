from game.players import BasePokerPlayer
from eqcalc.search import searcher as SS
from eqcalc.state import State
from game.engine.card import Card
from subagent.preflop import preflopper as PRE
from subagent.postflop import postflopper as POST
from eqcalc.deep import *

class MyPlayer(BasePokerPlayer):
    def __init__(self, debug = False, showhand = False, **kwargs):
        self.isBB = None
        self.debug = debug
        self.showhand = showhand

        self.s2suit = {s: i for i, s in enumerate(list("CDHS"))}
        self.s2rank = {s: i + 2 for i, s in enumerate(list("23456789TJQKA"))}

    def transform(self, msgs):
        # no need for FOLD or CALLIN
        ans, called = [], False
        for msg in msgs:
            if msg['action'] == 'CALL':
                if called: ans.append(SIGCALL)
                else:
                    if msg['paid'] > 0: ans.append(10)  # LIMP
                    else: ans.append(0) # CHECK
            elif msg['action'] == 'FOLD':
                ans.append(SIGFOLD)
            else:
                if msg['amount'] > 150: ans.append(1)
                else: ans.append(msg['amount'])
        return ans

    def declare_action(self, valid_actions, hole_card, round_state):
        self.valids = valid_actions
        if self.allined: return self.A()

        BBchip = self.my if self.isBB else self.opp

        if round_state['street'] == 'preflop':
            self.actions = self.transform(round_state['action_histories']['preflop'][2:])
            action = self.pre.act(BBchip, self.turn, self.hand, *self.actions)
            self.actions.append(action)
            return self.act(action)
        else: # POSTFLOP
            street = round_state['street']
            self.actions = self.transform(round_state['action_histories'][street])
            action = self.post.act(BBchip, self.turn, self.hand, *self.actions)
            self.actions.append(action)
            return self.act(action)

    def act(self, action):
        if action == SIGCALLIN: return self.A()
        if action == 1: return self.A()
        if action == SIGCALL: return self.C()
        if action == SIGFOLD: return self.F()
        if action == 0: return self.C()
        return self.R(action)

    def R(self, x):
        if self.debug: print("RAISE")
        if len(self.valids) == 2 or self.valids[2]["amount"]["max"] == -1: return self.C()
        if self.valids[2]["amount"]["min"] > x: return self.C()
        return self.valids[2]["action"], min(x, self.valids[2]["amount"]["max"])

    def CF(self):
        call = self.valids[1]["amount"] == 0
        return self.C() if call else self.F()

    def C(self):
        if self.debug: print("CALL")
        x = self.valids[1]
        return x["action"], x["amount"]

    def F(self):
        if self.debug: print("FOLD")
        x = self.valids[0]
        return x["action"], x["amount"]

    def A(self):
        self.allined = True
        if self.debug: print(f"ALLIN")
        if len(self.valids) == 2 or self.valids[2]["amount"]["max"] == -1: return self.C()
        x = self.valids[2]
        return x["action"], x["amount"]["max"]

    def receive_game_start_message(self, game_info):
        self.isBB = None

    def s2c(self, s):
        return self.s2suit[s[0]], self.s2rank[s[1]]

    def receive_round_start_message(self, round_count, hole_card, seats):
        if self.showhand: print(hole_card)
        self.hand = tuple(sorted((self.s2c(c) for c in hole_card)))
        self.isBB = seats[0]["uuid"] == self.uuid if (self.isBB is None) else (not self.isBB)
        self.turn = 19 - round_count
        self.allined = False

    def receive_street_start_message(self, street, round_state):
        rs = round_state["seats"]
        for pos in range(len(rs)):
            s = rs[pos]
            if s["uuid"] == self.uuid:
                self.pos = pos
                self.my = s["stack"]
            else:
                self.opp = s["stack"]
        
        rs = round_state["pot"]
        self.pot = rs["main"]["amount"]

        rs = round_state["community_card"]
        self.comm = [self.s2c(c) for c in rs]

        if round_state["street"] == "preflop":
            self.pre = PRE(debug = self.debug)
        elif round_state["street"] == "flop":
            BBr, SBr = self.pre.ranges(*self.actions)
            if self.isBB: self.post = POST(BBr, SBr, self.comm, BBincl = self.hand) 
            else: self.post = POST(BBr, SBr, self.comm, SBincl = self.hand, debug = self.debug) 
        else:
            BBr, SBr = self.pre.ranges(*self.actions)
            if self.isBB: self.post = POST(BBr, SBr, self.comm, BBincl = self.hand) 
            else: self.post = POST(BBr, SBr, self.comm, SBincl = self.hand, debug = self.debug) 

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def quiet_ai():
    return MyPlayer()

def show_ai():
    return MyPlayer(showhand = True)

def test_ai():
    return MyPlayer(debug = True, showhand = True)

def setup_ai():
    return MyPlayer(debug = True)
