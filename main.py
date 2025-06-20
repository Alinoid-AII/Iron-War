import pygame
from game.controllers.game_controller import GameController

if __name__ == "__main__":
    pygame.init()
    GameController().run()