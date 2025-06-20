import pygame
import sys
from ..models.game_state import GameState
from ..models.game_model import GameModel
from ..views.game_view import GameView

class GameController:
    def __init__(self):
        self.model = GameModel()
        self.view = GameView(self.model)
        self.running = True

    def run(self):
        while self.running:
            if not self.handle_events():
                break
                
            if self.model.state == GameState.GAME:
                self.model.update_keys()
                self.model.update_game()
            
            self.view.draw()
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        mouse_clicked = False
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.model.state == GameState.GAME:
                        self.model.state = GameState.PAUSE
                    elif self.model.state == GameState.PAUSE:
                        self.model.state = GameState.GAME
        
        self.model.keys = pygame.key.get_pressed()
        
        if self.model.state == GameState.MENU:
            self.handle_menu_events(mouse_pos, mouse_clicked)
        elif self.model.state == GameState.MAP_SELECT:
            self.handle_map_select_events(mouse_pos, mouse_clicked)
        elif self.model.state == GameState.TANK_SELECT:
            self.handle_tank_select_events(mouse_pos, mouse_clicked)
        elif self.model.state == GameState.PAUSE:
            self.handle_pause_events(mouse_pos, mouse_clicked)
        elif self.model.state == GameState.GAME_OVER:
            self.handle_game_over_events(mouse_pos, mouse_clicked)
        elif self.model.state == GameState.VICTORY:
            self.handle_victory_events(mouse_pos, mouse_clicked)
        
        return True

    def handle_menu_events(self, mouse_pos, mouse_clicked):
        for button in self.view.menu_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Играть":
                    self.model.state = GameState.MAP_SELECT
                elif button.text == "Выход":
                    self.running = False
                    return

    def handle_map_select_events(self, mouse_pos, mouse_clicked):
        for i, button in enumerate(self.view.map_select_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                self.model.selected_map = i
                self.model.state = GameState.TANK_SELECT
        
        self.view.back_button.check_hover(mouse_pos)
        if self.view.back_button.is_clicked(mouse_pos, mouse_clicked):
            self.model.state = GameState.MENU

    def handle_tank_select_events(self, mouse_pos, mouse_clicked):
        for btn in self.view.tank_select_buttons:
            btn.is_selected = False
        
        for i, button in enumerate(self.view.tank_select_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                self.model.selected_tank = i
                button.is_selected = True
        
        if 0 <= self.model.selected_tank < len(self.view.tank_select_buttons):
            self.view.tank_select_buttons[self.model.selected_tank].is_selected = True
        
        self.view.start_button.check_hover(mouse_pos)
        if self.view.start_button.is_clicked(mouse_pos, mouse_clicked):
            self.model.init_game()
            self.model.state = GameState.GAME
        
        self.view.back_button.check_hover(mouse_pos)
        if self.view.back_button.is_clicked(mouse_pos, mouse_clicked):
            self.model.state = GameState.MAP_SELECT

    def handle_pause_events(self, mouse_pos, mouse_clicked):
        for button in self.view.pause_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Продолжить":
                    self.model.state = GameState.GAME
                elif button.text == "Выход":
                    self.model.state = GameState.MAP_SELECT
                    return

    def handle_game_over_events(self, mouse_pos, mouse_clicked):
        for button in self.view.game_over_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Заново":
                    self.model.reset()                    
                    self.model.init_game()
                    self.model.state = GameState.GAME
                elif button.text == "Выход":
                    self.model.state = GameState.MAP_SELECT
                    return

    def handle_victory_events(self, mouse_pos, mouse_clicked):
        for button in self.view.victory_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Заново":
                    self.model.init_game()
                    self.model.state = GameState.GAME
                elif button.text == "Выход":
                    self.model.state = GameState.MAP_SELECT
                    return