from game.players import BasePokerPlayer
from eqcalc.search import searcher as SS
from eqcalc.state import State
from game.engine.card import Card
from pre.equireader import Equireader as EQ


class MyPlayer(BasePokerPlayer):
    def __init__(self, debug = False, showhand = False):
        self.SS = SS()
        self.isBB = None
        self.EQ = EQ()
        self.debug = debug
        self.showhand = showhand

    def declare_action(self, valid_actions, hole_card, round_state):
        self.valids = valid_actions
        isFirstAct, self.isFirstAct = self.isFirstAct, False
        if round_state['street'] == 'preflop':
            if not isFirstAct:
                return self.A()
            # if self.isWin():
            #    return self.F()
            if self.isBB:
                SBraise = round_state['action_histories']['preflop'][2]['amount']
                v, a, c = self.SS.FR(SBraise, State(self.my, turn = self.turn, equitizer = self.EQ))

                # switch c[hand] : F, C, A 
                myh = self.SS.h2h2i(self.cards)
                if self.debug: print(f"[DEBUG] BB: myh = {myh}, c[myh] = {c[myh]}, c = \n{c}\nshoving: {self.SS.r2s(c)}")
                if c[myh] == 2: return self.A()
                else: return self.C() if c[myh] == 1 else self.F()
            else:
                SBraise = 1000
                v, a, c = self.SS.FR(SBraise, State(self.opp, turn = self.turn, equitizer = self.EQ))

                # if hand <= a : A else F
                myh = self.SS.h2h2i(self.cards)
                if self.debug: print(f"[DEBUG] SB: myh = {myh}, a = {a}")
                return self.A() if myh <= a else self.F()
        else:
            return self.CF() # temp

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
        if self.debug: print(f"ALLIN")
        if len(self.valids) == 2 or self.valids[2]["amount"]["max"] == -1: return self.C()
        x = self.valids[2]
        return x["action"], x["amount"]["max"]

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        if self.showhand: print(hole_card)
        self.cards = [Card.from_str(c) for c in hole_card]
        self.isBB = seats[0]["uuid"] == self.uuid if self.isBB is None else not self.isBB
        self.turn = 20 - round_count

    def receive_street_start_message(self, street, round_state):
        self.isFirstAct = True

        rs = round_state["seats"]
        for pos in range(len(rs)):
            s = rs[pos]
            if s["uuid"] == self.uuid:
                self.pos = pos
                self.my = s["stack"]
            else:
                self.opp = s["stack"]

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def quiet_ai():
    return MyPlayer()

def test_ai():
    return MyPlayer(debug = True, showhand = False)

def setup_ai():
    return MyPlayer()
