import math
import random
import pygame
from .game_object import GameObject
from .game_state import GameState

class Tank(GameObject):
    DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    TANK_STATS = {
        "light": {"player_speed": 3, "enemy_speed": 1.5, "player_hp": 6, "enemy_hp": 2.5,
                  "player_damage": 1.5, "enemy_damage": 0.5, "scale": 1.2},
        "middle": {"player_speed": 2, "enemy_speed": 1, "player_hp": 8, "enemy_hp": 3.5,
                   "player_damage": 2, "enemy_damage": 1, "scale": 1.3},
        "heavy": {"player_speed": 1, "enemy_speed": 1, "player_hp": 10, "enemy_hp": 5,
                  "player_damage": 3, "enemy_damage": 2, "scale": 1.5}
    }
    SHOOTING_DISTANCE = 300

    def __init__(self, tank_type, px, py, direct, keyList=None, is_enemy=False):
        self._type = tank_type
        self._is_enemy = is_enemy
        self._rect = pygame.Rect(px, py, 32, 32)
        self._direct = direct
        self._collision_rect = pygame.Rect(px, py, 16, 16)
        
        stats = self.TANK_STATS[tank_type]
        prefix = "enemy_" if is_enemy else "player_"
        self._moveSpeed = stats[f"{prefix}speed"]
        self._hp = stats[f"{prefix}hp"]
        self._bulletDamage = stats[f"{prefix}damage"]
        
        if is_enemy:
            self._move_timer = 0
            self._current_move_duration = 0
            self._last_direction_change = 0
            self._stuck_counter = 0
            self._last_position = (px, py)
            self._avoidance_mode = False
            self._avoidance_direction = random.choice([-1, 1])
        else:
            self._keyLEFT = keyList[0]
            self._keyRIGHT = keyList[1]
            self._keyUP = keyList[2]
            self._keyDOWN = keyList[3]
            self._keySHOT = keyList[4]
        
        self._shotTimer = 0
        self._shotDelay = 50
        self._bulletSpeed = 5

    @property
    def tank_type(self):
        return self._type
        
    @property
    def is_enemy(self):
        return self._is_enemy
        
    @property
    def rect(self):
        return self._rect
        
    @property
    def direct(self):
        return self._direct
        
    @property
    def hp(self):
        return self._hp
        
    @hp.setter
    def hp(self, value):
        self._hp = value

    def reset(self):
        self._shotTimer = 0
        if self._is_enemy:
            self._move_timer = 0
            self._current_move_duration = 0
            self._stuck_counter = 0
            self._avoidance_mode = False

    def update(self, model):
        if model.state != GameState.GAME:
            return
            
        old_pos = self._rect.topleft
        
        if not self._is_enemy:
            self._player_controls(model)
        else:
            self._ai_controls(model)
        
        self._collision_rect.center = self._rect.center
        
        collision_occurred = self._check_collision(model)
        
        if collision_occurred:
            self._rect.topleft = old_pos
            self._collision_rect.center = self._rect.center
            if self._is_enemy:
                self._handle_collision_response()
        
        if self._is_enemy:
            self._check_stuck(old_pos)

        if self._shotTimer > 0:
            self._shotTimer -= 1

    def _player_controls(self, model):
        if model.keys[self._keyLEFT]:
            self._rect.x -= self._moveSpeed
            self._direct = 3
        elif model.keys[self._keyRIGHT]:
            self._rect.x += self._moveSpeed
            self._direct = 1
        elif model.keys[self._keyUP]:
            self._rect.y -= self._moveSpeed
            self._direct = 0
        elif model.keys[self._keyDOWN]:
            self._rect.y += self._moveSpeed
            self._direct = 2

        if model.keys[self._keySHOT] and self._shotTimer == 0:
            self.shoot(model)

    def _ai_controls(self, model):
        player = self._find_player(model)
        if not player:
            return

        dx = player.rect.centerx - self._rect.centerx
        dy = player.rect.centery - self._rect.centery

        is_facing_player = False
        if self._direct == 0 and dy < 0 and abs(dy) > abs(dx):
            is_facing_player = True
        elif self._direct == 1 and dx > 0 and abs(dx) > abs(dy):
            is_facing_player = True
        elif self._direct == 2 and dy > 0 and abs(dy) > abs(dx):
            is_facing_player = True
        elif self._direct == 3 and dx < 0 and abs(dx) > abs(dy):
            is_facing_player = True


        distance = math.sqrt(dx**2 + dy**2)
        if is_facing_player and distance < self.SHOOTING_DISTANCE and self._shotTimer == 0:
            self.shoot(model)

        if self._avoidance_mode:
            self._avoid_obstacle()
        else:
            self._chase_player(player)

    def _avoid_obstacle(self):
        current_time = pygame.time.get_ticks()
        self._avoidance_timer -= 1
        
        if self._avoidance_timer <= 0:
            self._avoidance_mode = False
            return
        
        if current_time - self._last_direction_change > 800:
            self._direct = (self._direct + self._avoidance_direction) % 4
            self._last_direction_change = current_time
            self._avoidance_timer = max(self._avoidance_timer, 45)
        
        dx, dy = self.DIRECTS[self._direct]
        self._rect.x += dx * self._moveSpeed
        self._rect.y += dy * self._moveSpeed

    def _chase_player(self, player):
        current_time = pygame.time.get_ticks()
        
        if current_time - self._last_direction_change < 500:
            dx, dy = self.DIRECTS[self._direct]
            self._rect.x += dx * self._moveSpeed
            self._rect.y += dy * self._moveSpeed
            return
        
        dx = player.rect.centerx - self._rect.centerx
        dy = player.rect.centery - self._rect.centery
        
        if abs(dx) > abs(dy) + 10:
            new_direct = 1 if dx > 0 else 3
        elif abs(dy) > abs(dx) + 10:
            new_direct = 2 if dy > 0 else 0
        else:
            new_direct = self._direct
        
        if new_direct != self._direct:
            self._direct = new_direct
            self._last_direction_change = current_time
        
        dx, dy = self.DIRECTS[self._direct]
        self._rect.x += dx * self._moveSpeed
        self._rect.y += dy * self._moveSpeed

    def _check_collision(self, model):
        if self._check_map_collision(model):
            return True
            
        for obj in model.get_objects():
            if (obj != self and not getattr(obj, 'is_bullet', False) and 
                self._rect.colliderect(obj.rect)):
                return True
                
        return False

    def _handle_collision_response(self):
        self._avoidance_mode = True
        self._avoidance_timer = 30
        self._avoidance_direction = random.choice([-1, 1])
        self._last_direction_change = pygame.time.get_ticks()

    def _check_stuck(self, old_pos):
        if old_pos == self._rect.topleft:
            self._stuck_counter += 1
            if self._stuck_counter > 30:
                self._handle_stuck()
                self._stuck_counter = 0
        else:
            self._stuck_counter = 0

    def _handle_stuck(self):
        self._avoidance_mode = True
        self._avoidance_timer = 45
        self._avoidance_direction = random.choice([-1, 1])
        self._direct = random.randint(0, 3)

    def _find_player(self, model):
        for obj in model.get_objects():
            if isinstance(obj, Tank) and not obj.is_enemy:
                return obj
        return None

    def shoot(self, model):
        dx = self.DIRECTS[self._direct][0] * self._bulletSpeed
        dy = self.DIRECTS[self._direct][1] * self._bulletSpeed
        model.create_bullet(self, self._rect.centerx, self._rect.centery, dx, dy, self._bulletDamage)
        self._shotTimer = self._shotDelay

    def _check_map_collision(self, model):
        map_data = model.maps[model.selected_map]
        offset = (self._collision_rect.x, self._collision_rect.y)
        tank_mask = pygame.Mask((self._collision_rect.width, self._collision_rect.height), True)
        return (map_data["collision_mask"].overlap(tank_mask, offset) or 
                map_data["impenetrable_mask"].overlap(tank_mask, offset))

    def damage(self, model, value):
        self._hp -= value
        if self._hp <= 0:
            model.remove_object(self)
            if self._is_enemy:
                model.enemies_killed += 1
                if model.enemies_killed >= model.enemies_total:
                    model.state = GameState.VICTORY
            else:
                model.state = GameState.GAME_OVER