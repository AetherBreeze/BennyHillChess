from sys import platform

# routes.py
NAMES_FILEPATH = "resources/txt/names.txt"

# game.py
MAX_VOLUME = 0.75
STOCKFISH_PATH = "resources/engines/stockfish/{}".format("stockfish_20011801_x64.exe" if platform == "win32" else "stockfish_200011801_x64")
VOLUME_MIDPOINT = -28 # hyperparameters chosen so that at 0, volume is 0.25; at -28, volume is ~0.66; and at -56, volume is basically maxed
VOLUME_STEEPNESS = 0.15
