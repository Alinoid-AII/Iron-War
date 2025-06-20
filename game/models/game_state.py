from enum import Enum

class GameState(Enum):
    MENU = 0
    MAP_SELECT = 1
    TANK_SELECT = 2
    GAME = 3
    PAUSE = 4
    GAME_OVER = 5
    VICTORY = 6