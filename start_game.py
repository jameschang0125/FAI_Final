import json
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai
from agents.my_player import setup_ai as my_ai
from agents.my_player import quiet_ai, test_ai, show_ai
from agents.deep_player import setup_ai as deep_ai
from agents.dps import setup_ai as dps_ai
from agents.dps import dps

# from extern.skywalker_2 import setup_ai as casper_ai

'''
from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
'''

from baseline5 import setup_ai as baseline5_ai

config = setup_config(max_round = 20, initial_stack = 1000, small_blind_amount = 5)
config.register_player(name = "me", algorithm = dps[3](showhand = True)) # deep_ai(showhand = True))
config.register_player(name = "opp", algorithm = console_ai())# dps[3](showhand = True)) # baseline5_ai())

## Play in interactive mode if uncomment
#config.register_player(name="me", algorithm=console_ai())
game_result = start_poker(config, verbose = 1)

print(json.dumps(game_result, indent = 4))
