import json
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai
from agents.my_player import setup_ai as my_ai

# from baseline0 import setup_ai as baseline0_ai

def func():
    config = setup_config(max_round = 20, initial_stack = 1000, small_blind_amount = 5)
    config.register_player(name = "p1", algorithm = my_ai())
    config.register_player(name = "p2", algorithm = random_ai())

    ## Play in interactive mode if uncomment
    #config.register_player(name="me", algorithm=console_ai())
    game_result = start_poker(config, verbose = 0)
    x, y = game_result["players"][0]["stack"], game_result["players"][1]["stack"]
    wins = 1 if x > y else (0.5 if x == y else 0)

print(json.dumps(game_result, indent = 4))