import json
import pygame
from .tank import Tank
from .bullet import Bullet
from .game_state import GameState

class GameModel:
    def __init__(self):
        self._state = GameState.MENU
        self._progress = self.load_progress()
        self.maps = self.load_map_data()
        self.selected_map = 0
        self.selected_tank = 1
        self._objects = []
        self._bullets = []
        self.enemies_killed = 0
        self.enemies_total = 0
        self.victory_counted = False
        self.keys = None

    def update_keys(self):
        self.keys = pygame.key.get_pressed()

    @property
    def state(self):
        return self._state
        
    @state.setter
    def state(self, value):
        if value == GameState.VICTORY:
            self.handle_victory()
        self._state = value
        
    @property
    def progress(self):
        return self._progress
        
    def get_objects(self):
        return self._objects.copy()
        
    def get_bullets(self):
        return self._bullets.copy()
        
    def add_object(self, obj):
        self._objects.append(obj)
        
    def remove_object(self, obj):
        if obj in self._objects:
            self._objects.remove(obj)
            
    def add_bullet(self, bullet):
        self._bullets.append(bullet)
        
    def remove_bullet(self, bullet):
        if bullet in self._bullets:
            self._bullets.remove(bullet)
            
    def create_bullet(self, parent, px, py, dx, dy, damage):
        bullet = Bullet(parent, px, py, dx, dy, damage)
        self.add_bullet(bullet)

    def load_progress(self):
        try:
            with open("progress.dat", "r") as f:
                data = json.load(f)
                return {
                    "completed_minsk": data.get("completed_minsk", False),
                    "completed_prokh": data.get("completed_prokh", False),
                    "light_tank_wins": data.get("light_tank_wins", 0),
                    "middle_tank_wins": data.get("middle_tank_wins", 0),
                    "heavy_tank_wins": data.get("heavy_tank_wins", 0)
                }
        except:
            return {
                "completed_minsk": False,
                "completed_prokh": False,
                "light_tank_wins": 0,
                "middle_tank_wins": 0,
                "heavy_tank_wins": 0
            }

    def save_progress(self):
        with open("progress.dat", "w") as f:
            json.dump(self.progress, f)

    def load_map_data(self):
        maps = [
            {
                "name": "Минск",
                "background": "resources\\img\\Minsk.jpg",
                "menu_bg": "resources\\img\\menu.png",
                "victory_bg": "resources\\img\\victory_Minsk.png",
                "sound": "resources\\audio\\Minsk.mp3",
                "impassable_colors": ["2B3838", "3F4843"],
                "impenetrable_colors": ["000000"],
                "player_start": (100, 275),
                "enemy_positions": [
                    (700, 100, 0), (600, 300, 1), (700, 500, 2),
                    (300, 200, 0), (400, 400, 1), (150, 80, 1)
                ],
                "block_positions": []
            },
            {
                "name": "Прохоровка",
                "background": "resources\\img\\Prokh.png",
                "menu_bg": "resources\\img\\menu.png",
                "victory_bg": "resources\\img\\victory_Prokh.png",
                "sound": "resources\\audio\\Prokhorovka.mp3",
                "impassable_colors": ["332B0F"],
                "impenetrable_colors": ["242320"],
                "player_start": (100, 275),
                "enemy_positions": [
                    (700, 200, 2), (650, 300, 2), (700, 500, 2),
                    (500, 200, 1), (500, 400, 1)
                ],
                "block_positions": []
            }
        ]
        return maps

    def create_collision_mask(self, surface, impassable_colors):
        hex_to_rgb = lambda hex_color: tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        colors_rgb = [hex_to_rgb(color) for color in impassable_colors]
        mask = pygame.Mask(surface.get_size(), False)
        for color in colors_rgb:
            temp_mask = pygame.mask.from_threshold(surface, color, threshold=(1, 1, 1))
            mask.draw(temp_mask, (0, 0))
        return mask

    def init_game(self):
        self.reset()
        self.victory_counted = False
        map_data = self.maps[self.selected_map]
        self.enemies_killed = 0
        self.enemies_total = len(map_data["enemy_positions"])
        
        pygame.mixer.music.load(map_data["sound"])
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1, 0.0)
        
        player_start = map_data["player_start"]
        tank_types = ["light", "middle", "heavy"]
        tank_type = tank_types[self.selected_tank]
        
        self.add_object(Tank(tank_type, player_start[0], player_start[1], 0, 
            (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE)))
        
        for pos in map_data["enemy_positions"]:
            x, y, enemy_type = pos
            enemy_tank_type = tank_types[enemy_type]
            self.add_object(Tank(enemy_tank_type, x, y, 3, is_enemy=True))

    def update_game(self):               
        self.keys = pygame.key.get_pressed()
        
        for bullet in self._bullets[:]:
            bullet.update(self)
        for obj in self._objects[:]:
            obj.update(self)

        self._objects = [obj for obj in self._objects if obj.hp > 0]

    def reset(self):
        self._objects = []
        self.enemies_killed = 0
        self.enemies_total = 0
        self.state = GameState.GAME

    def handle_victory(self):
        if not self.victory_counted:
            if self.selected_map == 0:
                self.progress["completed_minsk"] = True
            else:
                self.progress["completed_prokh"] = True
            
            if self.selected_tank == 0:
                self.progress["light_tank_wins"] += 1
            elif self.selected_tank == 1:
                self.progress["middle_tank_wins"] += 1
            elif self.selected_tank == 2:
                self.progress["heavy_tank_wins"] += 1
            self.save_progress()
            self.victory_counted = True

    def get_collision_grid(self):
        map_data = self.maps[self.selected_map]
        grid_size = 16
        grid_width = 750 // grid_size
        grid_height = 750 // grid_size
        
        grid = [[0] * grid_width for _ in range(grid_height)]
        
        for y in range(grid_height):
            for x in range(grid_width):
                px = x * grid_size + grid_size // 2
                py = y * grid_size + grid_size // 2
                
                if (map_data["collision_mask"].get_at((px, py))) or \
                   (map_data["impenetrable_mask"].get_at((px, py))):
                    grid[y][x] = 1
        
        return grid