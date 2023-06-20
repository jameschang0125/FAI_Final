from game.players import BasePokerPlayer
from src.eqcalc.search import searcher as SS
from src.eqcalc.state import State
from src.util.card import Card
from src.pre.equireader import Equireader as EQ
from src.eqcalc.presearch import presearcher as pre
from src.eqcalc.postsearch import postsearcher as post

class MyPlayer(BasePokerPlayer):
    def __init__(self, debug = False, showhand = False, **kwargs):
        '''
        kwargs :
        - pre
            - prekeeprate   : (default: 0.5)
            - predrawrate   : (default: 0.1)
            - preactfunc    : (default: None)
            - prepen        : used in searcher, penalize C - C (default: 0.95)
        - post
            - postkeeprate  : (default: 0.5)
            - postdrawrate  : (default: 0.2)
            - postactfunc   : (default: None)
            - postnSearch   : (default: 3)
            - postSBaggr    : (default: )
            - postBBaggr    : (default: )
            - postslowp     : (default: )
            - postCCaward   : (default: )
        '''

        self.pre = pre(debug = debug, **kwargs)
        self.post = post(debug = debug, **kwargs)
        self.isBB = None
        self.debug = debug
        self.showhand = showhand

        self.s2suit = {s: i for i, s in enumerate(list("CDHS"))}
        self.s2rank = {s: i + 2 for i, s in enumerate(list("23456789TJQKA"))}

        self.ignoreTL = True

    def declare_action(self, valid_actions, hole_card, round_state):
        self.valids = valid_actions
        
        if self.allined: return self.A()

        try:
            if round_state['street'] == 'preflop':
                if self.isBB:
                    rsize = round_state['action_histories']['preflop'][2]['amount']
                    act, self.myr, self.oppr = self.pre.calc(self.my, self.turn, rsize, self.cards)
                    # if self.debug: print(f"[DEBUG] BB: myh = {myh}, c[myh] = {c[myh]}, c = \n{c}\nshoving: {self.SS.r2s(c)}")
                    if act == 2: return self.A()
                    else: return self.C() if act == 1 else self.F()
                else:
                    rsize = 1000
                    act, self.oppr, self.myr = self.pre.calc(self.opp, self.turn, rsize, self.cards, BB = False)
                    return self.A() if act else self.F()
            else: # POSTFLOP BB
                street = round_state['street']
                rsize, SB_C = round_state['action_histories'][street][0]['amount'], False
                if rsize == 0: 
                    rsize, SB_C = 1000, True # A
                act_C, act_R, self.myr, self.oppr = self.post.calc(self.my, self.turn, self.pot, rsize, \
                                                        self.myr, self.cards, self.oppr, self.comm)
                act = act_C if SB_C else act_R
                return self.A() if act == 1 else self.CF()
        except:
            return self.CF()

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
        self.cards = tuple(sorted((self.s2c(c) for c in hole_card)))
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
    return MyPlayer()
