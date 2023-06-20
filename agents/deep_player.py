from game.players import BasePokerPlayer
from eqcalc.search import searcher as SS
from eqcalc.state import State
from game.engine.card import Card
from subagent.preflop import preflopper as PRE
from subagent.postflop import postflopper as POST
from eqcalc.deep import *
from subagent.heuristics import *
from util.shower import Shower
from pre.equitizer import Equitizer as EQ
import json

class DeepPlayer(BasePokerPlayer):
    def __init__(self, debug = False, showhand = False, 
                 preTemplate = None, postTemplate = None, printerror = True, **kwargs):
        self.isBB = None
        self.debug = debug
        self.showhand = showhand
        self.printerror = printerror

        self.s2suit = {s: i for i, s in enumerate(list("CDHS"))}
        self.s2rank = {s: i + 2 for i, s in enumerate(list("23456789TJQKA"))}

        self.ignoreTL = True

        self.preTemplate = PRE if preTemplate is None else preTemplate
        self.postTemplate = POST if postTemplate is None else postTemplate

    def transform(self, msgs):
        # no need for FOLD or CALLIN
        ans, shoved = [], False
        for i, msg in enumerate(msgs):
            if msg['action'] == 'CALL':
                if i > 0: 
                    if shoved: ans.append(SIGCALLIN)
                    else: ans.append(SIGCALL)
                else:
                    if msg['paid'] > 0: ans.append(10)  # LIMP
                    else: ans.append(0) # CHECK
            elif msg['action'] == 'FOLD':
                ans.append(SIGFOLD)
            else:
                if msg['amount'] > 150: 
                    ans.append(1) # ALLIN
                    shoved = True
                else: ans.append(int(msg['amount']))
            
        if self.debug: print(f"[DEBUG][player.transform] msgs = {msgs}, ans = {ans}")
        return ans
    
    def declare_action(self, *args):
        return self._declare_action(*args)

    def _declare_action(self, valid_actions, hole_card, round_state):
        try:
            if self.debug: print(f"[DEBUG][player.declare...] street = {round_state['street']}")
            self.valids = valid_actions
            if self.allined: return self.A()

            BBchip = self.my if self.isBB else self.opp

            if round_state['street'] == 'preflop':
                tmp = EQ._iswin(self.turn, BBchip)
                if tmp is not None:
                    self.sleep = True
                    if tmp == 1:
                        return self.F() if self.isBB else self.A()
                    if tmp == 0:
                        return self.A() if self.isBB else self.F()

                self.actions = self.transform(round_state['action_histories']['preflop'][2:])
                if self.debug: print(f"[DEBUG][player.declare_action] self.actions = {self.actions}")
                action = self.pre.act(BBchip, self.turn, self.hand, *self.actions)
                # self.actions.append(action)
                return self.act(action)
            else: # POSTFLOP
                street = round_state['street']
                streetid = STREETFLOP if street == 'flop' else (STREETTURN if street == 'turn' else STREETRIVER)
                self.actions = self.transform(round_state['action_histories'][street])
                if self.debug: print(f"[DEBUG][player.declare_action] self.actions = {self.actions}")
                action = self.post.act(BBchip, self.turn, self.hand, self.pot, *self.actions, street = streetid)
                # self.actions.append(action)
                return self.act(action)
        except Exception as e:
            if self.printerror:
                print("\n----------------------------------")
                print(repr(e))
                try:
                    print(self.pre.transform(self.actions, self.pre.cur))
                except:
                    pass
                try:
                    print(self.post.transform(self.actions, self.post.cur))
                except:
                    pass
                print(round_state)
            return self.CF()

    def act(self, action):
        if self.debug: print(f"[DEBUG][player.act] {action}")
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
        self.hand = tuple(sorted((self.s2c(c) for c in hole_card)))
        self.isBB = seats[0]["uuid"] == self.uuid if (self.isBB is None) else (not self.isBB)
        self.turn = 21 - round_count
        self.allined = False
        self.sleep = False
        if self.debug or self.showhand: print(f"[DEBUG] self.hand = {Shower.h2s(self.hand)}")

        for pos in range(len(seats)):
            s = seats[pos]
            if s["uuid"] == self.uuid:
                self.pos = pos
                self.my = s["stack"] + (10 if self.isBB else 5)
            else:
                self.opp = s["stack"] + (5 if self.isBB else 10)
        
        tmp = (2000 - self.my - self.opp) / 2
        self.my += tmp
        self.opp += tmp
        self.pre, self.post = None, None
        
        if self.debug: print(f"[DEBUG][player.roundstart] {self.my} vs {self.opp}")

    def receive_street_start_message(self, *args):
        return self._receive_street_start_message(*args)

    def _receive_street_start_message(self, street, round_state):
        if self.debug: print(f"[DEBUG][player.receive...] street = {street}")

        if EQ._iswin(self.turn, self.my) is not None: return
        if self.allined or self.sleep: return

        rs = round_state["pot"]
        self.pot = rs["main"]["amount"]

        rs = round_state["community_card"]
        self.comm = [self.s2c(c) for c in rs]

        # [DEBUG] tmp
        try:
            if street == "preflop":
                self.pre = self.preTemplate(debug = self.debug)
            elif street == "flop":
                self.actions = self.transform(round_state['action_histories']['preflop'][2:])
                if self.debug: print(f"[DEBUG][player.receive...] self.actions = {self.actions}")
                BBr, SBr = self.pre.ranges(self.hand, *self.actions)
                if self.isBB: self.post = self.postTemplate(BBr, SBr, self.comm, BBincl = self.hand, debug = self.debug) 
                else: self.post = self.postTemplate(BBr, SBr, self.comm, SBincl = self.hand, debug = self.debug) 
            else:
                minSamples = 50 if street == "turn" else 26
                prev = "flop" if street == "turn" else "turn"
                self.actions = self.transform(round_state['action_histories'][prev])
                if self.debug: print(f"[DEBUG][player.receive...] self.actions = {self.actions}")
                BBr, SBr = self.post.ranges(self.hand, *self.actions, minSamples = minSamples)
                if self.isBB: self.post = self.postTemplate(BBr, SBr, self.comm, BBincl = self.hand, debug = self.debug) 
                else: self.post = self.postTemplate(BBr, SBr, self.comm, SBincl = self.hand, debug = self.debug) 
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            if self.printerror:
                print(f"[STACK] {self.my} vs {self.opp}")
                print(f"[VALUE] {self.allined}, {self.sleep}")
                print(f"[OTHER] {street}, {round_state}, {self.actions}")
                try:
                    print(f"preTree: {json.dumps(self.pre.gt.getTree(), indent = 4)}")
                except Exception as e2:
                    print(repr(e2))
                try:
                    print(f"postTree: {json.dumps(self.post.gt.getTree(), indent = 4)}")
                except Exception as e2:
                    print(repr(e2))
                print(repr(e))


    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def setup_ai(debug = False, showhand = False):
    return DeepPlayer(debug = debug, showhand = showhand)
