import pygame
from .game_state import GameState
from .tank import Tank

class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        self._parent = parent
        self._px, self._py = px, py
        self._dx, self._dy = dx, dy
        self._damage = damage
        self._radius = 2

    @property
    def px(self):
        return self._px
        
    @property
    def py(self):
        return self._py
        
    @property
    def radius(self):
        return self._radius

    def update(self, model):
        if model.state != GameState.GAME:
            return
            
        self._px += self._dx
        self._py += self._dy

        map_data = model.maps[model.selected_map]
        bullet_mask = pygame.Mask((self._radius*2, self._radius*2), True)
        bullet_rect = pygame.Rect(self._px-self._radius, self._py-self._radius, 
                                self._radius*2, self._radius*2)
        offset = (bullet_rect.x, bullet_rect.y)
        
        if map_data["impenetrable_mask"].overlap(bullet_mask, offset):
            model.remove_bullet(self)
            return
            
        if self._px < 0 or self._px > 750 or self._py < 0 or self._py > 750:
            model.remove_bullet(self)
        else:
            for obj in model.get_objects():
                if obj != self._parent and obj.rect.collidepoint(self._px, self._py):
                    if isinstance(obj, Tank):
                        obj.damage(model, self._damage)
                    model.remove_bullet(self)
                    break