# routes.py
NAMES_FILEPATH = "resources/txt/names.txt"

# game.py
MAX_VOLUME = 0.75
STOCKFISH_PATH = "resources/engines/stockfish/stockfish_20011801_x64.exe"
VOLUME_MIDPOINT = -28 # hyperparameters chosen so that at 0, volume is 0.25; at -28, volume is ~0.66; and at -56, volume is basically maxed
VOLUME_STEEPNESS = 0.15
