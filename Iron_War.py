import pygame
import math
import sys
import json
pygame.init()

progress = {
    "completed_minsk": False,
    "completed_prokh": False,
    "light_tank_wins": 0,
    "middle_tank_wins": 0,    
    "heavy_tank_wins": 0
}

def save_progress():
    with open("progress.dat", "w") as f:
        json.dump(progress, f)

def load_progress():
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

progress = load_progress()

victory_counted = False

info = pygame.display.Info()
WIDTH, HEIGHT = 750, 750
FPS = 60
TILE = 32

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 100, 255)
LIGHT_RED = (255, 100, 100)
LIGHT_GREEN = (100, 255, 100)

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IRON WAR")
clock = pygame.time.Clock()

#вверх, вправо, вниз, влево
DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

bullets = []
objects = []
enemies_killed = 0
enemies_total = 0

MENU = 0
MAP_SELECT = 1
TANK_SELECT = 2
GAME = 3
PAUSE = 4
GAME_OVER = 5
VICTORY = 6
game_state = MENU

selected_map = 0  # 0=Минск, 1=Прохоровка
selected_tank = 1  # 0=Light, 1=Middle, 2=Heavy


maps = [
    {
        "name": "Минск",
        "background": "img\\Minsk.jpg",
        "menu_bg": "img\\menu.png",
        "victory_bg": "img\\victory_Minsk.png",
        "sound": "audio\\Minsk.mp3",
        "impassable_colors": ["2B3838", "3F4843"],
        "impenetrable_colors": ["000000"],
        "player_start": (100, 275),
        "enemy_positions": [
            (700, 100, 0),  #x, y, тип танка
            (600, 300, 1),
            (700, 500, 2),
            (300, 200, 0),
            (400, 400, 1),
            (150, 80, 1)
        ],
        "block_positions": []
    },
    {
        "name": "Прохоровка",
        "background": "img\\Prokh.png",
        "menu_bg": "img\\menu.png",
        "victory_bg": "img\\victory_Prokh.png",
        "sound": "audio\\Prokhorovka.mp3",
        "impassable_colors": ["332B0F"],
        "impenetrable_colors": ["242320"],
        "player_start": (100, 275),
        "enemy_positions": [
            (700, 200, 2),
            (650, 300, 2),
            (700, 500, 2),
            (500, 200, 1),
            (500, 400, 1)
        ],
        "block_positions": [
        ]
    }
]

current_map = maps[selected_map]
background = pygame.image.load(current_map["background"]).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

menu_bg = pygame.image.load(current_map["menu_bg"]).convert()
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))

star_img = pygame.image.load('img/star.png').convert_alpha()
star_img = pygame.transform.scale(star_img, (20, 20))

victory_bg = pygame.image.load(current_map["victory_bg"]).convert()
victory_bg = pygame.transform.scale(victory_bg, (WIDTH, HEIGHT))

medal_minsk = pygame.image.load('img/medal.png').convert_alpha()
medal_minsk = pygame.transform.scale(medal_minsk, (140, 182.9))

medal_minsk_progress = pygame.image.load('img/medal_minsk_pr.png').convert_alpha()
medal_minsk_progress = pygame.transform.scale(medal_minsk_progress, (140, 202))

medal_prokh = pygame.image.load('img/medal_prokh.png').convert_alpha()
medal_prokh = pygame.transform.scale(medal_prokh, (140, 206))

#аудио
pygame.mixer.init(44100, -16, 2, 2048)

shot_sound = pygame.mixer.Sound("audio/shot.mp3")
shot_sound.set_volume(0.3)

#маска препятствий по цветам
def create_collision_mask(surface, IMPASSABLE_COLORS):
    mask = pygame.Mask((surface.get_width(), surface.get_height()))
    hex_to_rgb = lambda hex_color: tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    impassable_colors = [hex_to_rgb(color) for color in IMPASSABLE_COLORS]
    
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            pixel_color = surface.get_at((x, y))[:3]
            if pixel_color in impassable_colors:
                mask.set_at((x, y), 1)
    
    return mask

collision_mask = create_collision_mask(background, current_map["impassable_colors"])
impenetrable_mask = create_collision_mask(background, current_map["impenetrable_colors"])


DEV_TRAPEZOID_COLOR = (200, 0, 0, 100)

def draw_development():
    base_width = 300
    top_width = 200
    trapezoid_height = 40
    
    #поверхность
    surf_size = max(base_width, trapezoid_height) * 2
    development_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)#для прозрачности
    
    left_offset = (base_width - top_width) // 2

    points = [
        (left_offset, surf_size//2 - trapezoid_height//2),            #верх-лево
        (left_offset + top_width, surf_size//2 - trapezoid_height//2), #верх-право
        (base_width, surf_size//2 + trapezoid_height//2),              #низ-право
        (0, surf_size//2 + trapezoid_height//2)                        #низ-лево
    ]
    
    pygame.draw.polygon(development_surf, DEV_TRAPEZOID_COLOR, points)
    
    font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 18)
    text = font.render("Development", True, WHITE)
    text_rect = text.get_rect(center=(base_width//2, surf_size//2))
    development_surf.blit(text, text_rect)
    
    rotated_surf = pygame.transform.rotate(development_surf, 45)
    
    offset_x = -rotated_surf.get_width() // 3.65
    offset_y = -rotated_surf.get_height() // 1.9
    
    window.blit(rotated_surf, (offset_x, offset_y))


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_selected = False
        
    def draw(self, surface):
        base_color = self.hover_color if (self.is_hovered or self.is_selected) else self.color
        
        pygame.draw.rect(surface, base_color, self.rect)

        border_color = (208, 217, 208)
        
        #верхняя и нижняя границы
        pygame.draw.line(surface, border_color, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)
        pygame.draw.line(surface, border_color, (self.rect.left, self.rect.bottom - 1), (self.rect.right, self.rect.bottom - 1), 3)
        
        #левая и правая границы
        pygame.draw.line(surface, border_color, (self.rect.left, self.rect.top), (self.rect.left, self.rect.bottom), 3)
        pygame.draw.line(surface, border_color, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom), 3)
        
        #закругленные углы
        pygame.draw.rect(surface, border_color, (self.rect.left, self.rect.top, 3, 3))
        pygame.draw.rect(surface, border_color, (self.rect.right - 3, self.rect.top, 3, 3))
        pygame.draw.rect(surface, border_color, (self.rect.left, self.rect.bottom - 3, 3, 3))
        pygame.draw.rect(surface, border_color, (self.rect.right - 3, self.rect.bottom - 3, 3, 3))
        
        font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 15)
        text_surface = font.render(self.text, True, (208, 217, 208))
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        #эффект нажатия
        if self.is_hovered or self.is_selected:
            text_rect.y += 2

            shadow_surface = font.render(self.text, True, (80, 80, 80))
            shadow_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 2))
            surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Tank:
    def __init__(self, color, px, py, direct, keyList, is_enemy=False):
        objects.append(self)
        self.type = 'tank'
        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.is_enemy = is_enemy
        self.collision_rect = pygame.Rect(px, py, TILE // 2, TILE // 2)

        if is_enemy:
            self.image = pygame.image.load('img/tanks/m_g.png').convert_alpha()
        else:
            self.image = pygame.image.load('img/tanks/m_u.png').convert_alpha()
        
        self.image = pygame.transform.scale(self.image, (TILE * 1.5, TILE * 1.5))
        
        self.moveSpeed = 2
        self.hp = 5
        self.shotTimer = 0
        self.shotDelay = 60
        self.bulletSpeed = 5
        self.bulletDamage = 1

        if not is_enemy:
            self.keyLEFT = keyList[0]
            self.keyRIGHT = keyList[1]
            self.keyUP = keyList[2]
            self.keyDOWN = keyList[3]
            self.keySHOT = keyList[4]

    def update(self):
        if game_state != GAME:
            return
            
        oldX, oldY = self.rect.topleft
        
        if not self.is_enemy:
            self.player_controls()
        else:
            self.ai_controls()
        
        self.collision_rect.center = self.rect.center
        
        if self.check_map_collision():
            self.rect.topleft = oldX, oldY
            self.collision_rect.center = self.rect.center
        
        if self.shotTimer > 0: 
            self.shotTimer -= 1

    def check_map_collision(self):
        offset = (self.collision_rect.x, self.collision_rect.y)
        tank_mask = pygame.Mask((self.collision_rect.width, self.collision_rect.height), True)
        return (collision_mask.overlap(tank_mask, offset) or 
                impenetrable_mask.overlap(tank_mask, offset))

    def player_controls(self):
        oldX, oldY = self.rect.topleft
        
        if keys[self.keyLEFT]:
            self.rect.x -= self.moveSpeed
            self.direct = 3
        elif keys[self.keyRIGHT]:
            self.rect.x += self.moveSpeed
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y -= self.moveSpeed
            self.direct = 0
        elif keys[self.keyDOWN]:
            self.rect.y += self.moveSpeed
            self.direct = 2

        for obj in objects:
            if obj != self and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.keySHOT] and self.shotTimer == 0:
            self.shoot()

    def ai_controls(self):
        player = self.find_player()
        if not player:
            return

        oldX, oldY = self.rect.topleft
        
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            dx, dy = dx/dist, dy/dist
            self.rect.x += dx * self.moveSpeed
            self.rect.y += dy * self.moveSpeed
            
            if abs(dx) > abs(dy):
                self.direct = 1 if dx > 0 else 3
            else:
                self.direct = 2 if dy > 0 else 0

        for obj in objects:
            if obj != self and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if self.shotTimer == 0 and dist < 300:
            self.shoot()

    def find_player(self):
        for obj in objects:
            if obj.type == 'tank' and not obj.is_enemy:
                return obj
        return None

    def shoot(self):
        dx = DIRECTS[self.direct][0] * self.bulletSpeed
        dy = DIRECTS[self.direct][1] * self.bulletSpeed
        Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)
        self.shotTimer = self.shotDelay
        
        if shot_sound:
            shot_sound.play()

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.direct * 90)
        window.blit(rotated_image, self.rect)

    def damage(self, value):
        global enemies_killed, game_state
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            if self.is_enemy:
                enemies_killed += 1
                if enemies_killed >= enemies_total:
                    game_state = VICTORY
            else:
                game_state = GAME_OVER

class Light(Tank):
    def __init__(self, color, px, py, direct, keyList, is_enemy=False):
        super().__init__(color, px, py, direct, keyList, is_enemy)
        
        if is_enemy:
            self.image = pygame.image.load('img\\tanks\l_g.png').convert_alpha()
            self.moveSpeed = 1.5
            self.hp = 2.5
            self.bulletDamage = 0.5            
        else:
            self.image = pygame.image.load('img\\tanks\l_u.png').convert_alpha()
            self.moveSpeed = 3
            self.hp = 6
            self.bulletDamage = 1.5

        self.image = pygame.transform.scale(self.image, (TILE * 1.2, TILE * 1.2))

class Middle(Tank):
    def __init__(self, color, px, py, direct, keyList, is_enemy=False):
        super().__init__(color, px, py, direct, keyList, is_enemy)

        if is_enemy:
            self.image = pygame.image.load('img/tanks/m_g.png').convert_alpha()
            self.moveSpeed = 1
            self.hp = 3.5
            self.bulletDamage = 1         
        else:
            self.image = pygame.image.load('img/tanks/m_u.png').convert_alpha()
            self.moveSpeed = 2
            self.hp = 8
            self.bulletDamage = 2            
        self.image = pygame.transform.scale(self.image, (TILE * 1.3, TILE * 1.3))        
        
class Heavy(Tank):
    def __init__(self, color, px, py, direct, keyList, is_enemy=False):
        super().__init__(color, px, py, direct, keyList, is_enemy)

        if is_enemy:
            self.image = pygame.image.load('img/tanks/h_g.png').convert_alpha()
            self.moveSpeed = 1
            self.hp = 5
            self.bulletDamage = 2          
        else:
            self.image = pygame.image.load('img/tanks/h_u.png').convert_alpha()
            self.moveSpeed = 1
            self.hp = 10
            self.bulletDamage = 3            
        self.image = pygame.transform.scale(self.image, (TILE * 1.5, TILE * 1.5))        

class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        bullets.append(self)
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage
        self.radius = 2

    def update(self):
        if game_state != GAME:
            return
            
        self.px += self.dx
        self.py += self.dy

        #проверка непробиваемых препятствий
        bullet_mask = pygame.Mask((self.radius*2, self.radius*2), True)
        bullet_rect = pygame.Rect(self.px-self.radius, self.py-self.radius, 
                                self.radius*2, self.radius*2)
        offset = (bullet_rect.x, bullet_rect.y)
        
        if impenetrable_mask.overlap(bullet_mask, offset):
            bullets.remove(self)
            return
            
        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                if obj != self.parent and obj.rect.collidepoint(self.px, self.py):
                    obj.damage(self.damage)
                    bullets.remove(self)
                    break

    def draw(self):
        pygame.draw.circle(window, YELLOW, (int(self.px), int(self.py)), self.radius)

class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block'
        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(window, GREEN, self.rect)
        pygame.draw.rect(window, BLACK, self.rect, 2)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)

def draw_stats():
    font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 24)
    enemies_text = font.render(f"Уничтожено: {enemies_killed}/{enemies_total}", True, WHITE)
    window.blit(enemies_text, (10, 10))
    
    player = None
    for obj in objects:
        if obj.type == 'tank' and not obj.is_enemy:
            player = obj
            break
            
    if player:
        health_text = font.render(f"Здоровье: {player.hp}", True, WHITE)
        window.blit(health_text, (10, 40))

def draw_menu():
    window.blit(menu_bg, (0, 0))
    
    for button in menu_buttons:
        button.draw(window)

def draw_map_selection():
    window.blit(menu_bg, (0, 0))
    
    title_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 40)
    title = title_font.render("ВЫБЕРИТЕ КАРТУ", True, (55, 59, 56))
    window.blit(title, (WIDTH//2 - title.get_width()//2, 200))
    
    for button in map_select_buttons:
        button.draw(window)
    
    if progress["completed_minsk"]:
        window.blit(medal_minsk_progress, (20, 300))
    if progress["completed_prokh"]:
        window.blit(medal_prokh, (WIDTH//2 + 20 + 180 + 10, 300))
    
    back_button.draw(window)

def draw_tank_selection():
    window.blit(menu_bg, (0, 0))
    title_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 40)
    title = title_font.render("ВЫБЕРИТЕ ТАНК", True, (55, 59, 56))
    window.blit(title, (WIDTH//2 - title.get_width()//2, 200))
    
    font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 20)
    
    light_stats = font.render(f"Побед: {progress['light_tank_wins']}", True, (43, 56, 56))
    middle_stats = font.render(f"Побед: {progress['middle_tank_wins']}", True, (43, 56, 56))    
    heavy_stats = font.render(f"Побед: {progress['heavy_tank_wins']}", True, (43, 56, 56))
    window.blit(light_stats, (70, 330))
    window.blit(middle_stats, (325, 330))
    window.blit(heavy_stats, (560, 330))
    
    #легкий
    light_desc = [
        "ЛЕГКИЙ ТАНК",
        "Скорость:",
        "Здоровье:",
        "Урон:"
    ]
    light_stars = [5, 3, 1]
    
    for i, line in enumerate(light_desc):
        text = font.render(line, True, (43, 56, 56))
        window.blit(text, (20, 360 + i*25))
        
        if i > 0:
            for j in range(light_stars[i-1]):
                window.blit(star_img, (20 + text.get_width() + 10 + j*25, 360 + i*25))
    
    #средний
    middle_desc = [
        "СРЕДНИЙ ТАНК",
        "Скорость:",
        "Здоровье:",
        "Урон:"
    ]
    middle_stars = [3, 4, 2]
    
    for i, line in enumerate(middle_desc):
        text = font.render(line, True, (43, 56, 56))
        window.blit(text, (270, 360 + i*25))
        
        if i > 0:
            for j in range(middle_stars[i-1]):
                window.blit(star_img, (270 + text.get_width() + 10 + j*25, 360 + i*25))
    
    #тяжелый
    heavy_desc = [
        "ТЯЖЕЛЫЙ ТАНК",
        "Скорость:",
        "Здоровье:",
        "Урон:"
    ]
    heavy_stars = [1, 5, 3]
    
    for i, line in enumerate(heavy_desc):
        text = font.render(line, True, (43, 56, 56))
        window.blit(text, (500, 360 + i*25))
        
        if i > 0:
            for j in range(heavy_stars[i-1]):
                window.blit(star_img, (500 + text.get_width() + 10 + j*25, 360 + i*25))
    
    for button in tank_select_buttons:
        button.draw(window)
    
    start_button.draw(window)
    back_button.draw(window)

def draw_pause():
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    window.blit(s, (0, 0))
    
    pause_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 50)
    pause_text = pause_font.render("ПАУЗА", True, WHITE)
    window.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 80))
    
    for button in pause_buttons:
        button.draw(window)

def draw_game_over():
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    window.blit(s, (0, 0))
    
    font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 50)
    text = font.render("ПОРАЖЕНИЕ", True, RED)
    window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))
    
    for button in game_over_buttons:
        button.draw(window)

def draw_victory():
    global victory_counted
    
    window.blit(victory_bg, (0, 0))
    
    victory_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 50)
    text = victory_font.render("ПОБЕДА!", True, GREEN)
    window.blit(text, (WIDTH//2 - text.get_width()//2, 75))

    if not victory_counted:
        if selected_map == 0:
            progress["completed_minsk"] = True
        else:
            progress["completed_prokh"] = True
        
        if selected_tank == 0:
            progress["light_tank_wins"] += 1
        elif selected_tank == 1:
            progress["middle_tank_wins"] += 1
        elif selected_tank == 2:
            progress["heavy_tank_wins"] += 1
         
        save_progress()
        victory_counted = True

    story_font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 18)
    
    if selected_map == 0:
        story_lines = [
            "Танковое наступление советской армии в Минске",
            "стало ключевым моментом в освобождении города.",
            "Благодаря слаженным действиям танковых бригад,",
            "советские войска прорвали оборону противника",
            "и освободили столицу Беларуси.",
            "",
            "Операция \"Багратион\", в ходе которой был",
            "освобожден Минск, считается одним из самых",
            "успешных наступлений в истории войн.",
            "Советские танковые соединения преодолели",
            "более 100 км за 6 дней, окружив и уничтожив",
            "крупную группировку немецких войск."
        ]

        medal_width, medal_height = medal_minsk.get_size()
        medal = medal_minsk
    else:
        story_lines = [
            "Танковое сражение под Прохоровкой",
            "стало кульминацией Курской битвы.",
            "12 июля 1943 года на поле боя",
            "сошлись сотни советских и немецких машин.",
            "Советские танкисты пошли в решительную лобовую",
            "атаку, чтобы остановить элитные дивизии СС.",
            "",
            "Обе стороны понесли огромные потери.",
            "Но советские войска сломили сопротивление,",
            "сорвав немецкую операцию \"Цитадель\".",
            "Этот подвиг стал переломным моментом,",
            "инициатива теперь была за Красной Армией."
        ]

        medal_width, medal_height = medal_prokh.get_size()
        medal = medal_prokh
    
    max_text_width = max(story_font.size(line)[0] for line in story_lines)
    text_height = len(story_lines) * 30
    
    
    #подложка под текст
    content_width = max_text_width + medal_width + 60
    content_height = max(text_height, medal_height) + 40
    
    content_surface = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
    content_surface.fill((0, 0, 0, 150))
    
    story_x = 20
    story_y = 20
    for i, line in enumerate(story_lines):
        text_surface = story_font.render(line, True, WHITE)
        content_surface.blit(text_surface, (story_x, story_y + i*30))
    
    medal_x = content_width - medal_width - 20
    medal_y = 20
    content_surface.blit(medal, (medal_x, medal_y))
    
    content_x = (WIDTH - content_width) // 2
    content_y = 150
    window.blit(content_surface, (content_x, content_y))
    
    for button in victory_buttons:
        button.draw(window)

def init_game():
    global bullets, objects, enemies_killed, enemies_total, background, victory_bg, collision_mask, impenetrable_mask
    
    map_data = maps[selected_map]
    
    background = pygame.image.load(map_data["background"]).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    victory_bg = pygame.image.load(map_data["victory_bg"]).convert()
    victory_bg = pygame.transform.scale(victory_bg, (WIDTH, HEIGHT))
    
    collision_mask = create_collision_mask(background, map_data["impassable_colors"])
    impenetrable_mask = create_collision_mask(background, map_data["impenetrable_colors"])
    
    bullets = []
    objects = []
    enemies_killed = 0
    enemies_total = len(map_data["enemy_positions"])
    
    pygame.mixer.music.load(map_data["sound"])
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1,0.0)    
    
    player_start = map_data["player_start"]
    if selected_tank == 0:
        Light('blue', player_start[0], player_start[1], 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    elif selected_tank == 1:
        Middle('blue', player_start[0], player_start[1], 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    elif selected_tank == 2:
        Heavy('blue', player_start[0], player_start[1], 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    
    for pos in map_data["enemy_positions"]:
        x, y, tank_type = pos
        if tank_type == 0:
            Light('red', x, y, 3, (), is_enemy=True)
        elif tank_type == 1:
            Middle('red', x, y, 3, (), is_enemy=True)
        elif tank_type == 2:
            Heavy('red', x, y, 3, (), is_enemy=True)
    
    for pos in map_data["block_positions"]:
        if len(pos) == 3:
            Block(pos[0], pos[1], pos[2])
        else:
            Block(pos[0], pos[1], TILE)


menu_buttons = [
    Button(WIDTH//2 - 100, 350, 200, 50, "Играть", (94, 95, 64), (115, 109, 83)),
    Button(WIDTH//2 - 100, 420, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
]

map_select_buttons = [
    Button(WIDTH//2 - 200, 300, 180, 50, "Минск", (43, 56, 56), (63, 72, 67)),
    Button(WIDTH//2 + 20, 300, 180, 50, "Прохоровка", (43, 56, 56), (63, 72, 67))
]

back_button = Button(WIDTH//2 - 100, 500, 200, 50, "Назад", (148, 47, 61), (204, 92, 107))

tank_select_buttons = [
    Button(50, 270, 150, 50, "Легкий", (43, 56, 56), (63, 72, 67)),
    Button(300, 270, 150, 50, "Средний", (43, 56, 56), (63, 72, 67)),
    Button(535, 270, 150, 50, "Тяжелый", (43, 56, 56), (63, 72, 67))
]

start_button = Button(WIDTH//2 - 100, 570, 200, 50, "Начать игру", (81, 102, 58), (131, 163, 96))

pause_buttons = [
    Button(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 50, "Продолжить", (81, 102, 58), (131, 163, 96)),
    Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
]

game_over_buttons = [
    Button(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 50, "Заново", (81, 102, 58), (131, 163, 96)),
    Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
]

victory_buttons = [
    Button(WIDTH//2 - 100, HEIGHT - 160, 200, 50, "Заново", (81, 102, 58), (131, 163, 96)),
    Button(WIDTH//2 - 100, HEIGHT - 90, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
]

#игровой цикл
running = True
mouse_clicked = False
keys = pygame.key.get_pressed()

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_clicked = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME:
                    game_state = PAUSE
                elif game_state == PAUSE:
                    game_state = GAME
    
    keys = pygame.key.get_pressed()
    
    if game_state == MENU:
        for button in menu_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Играть":
                    game_state = MAP_SELECT
                elif button.text == "Выход":
                    running = False
    
    elif game_state == MAP_SELECT:
        for i, button in enumerate(map_select_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                selected_map = i

                current_map = maps[selected_map]
                menu_bg = pygame.image.load(current_map["menu_bg"]).convert()
                menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
                game_state = TANK_SELECT
        
        back_button.check_hover(mouse_pos)
        if back_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = MENU
    
    elif game_state == TANK_SELECT:
        for btn in tank_select_buttons:
            btn.is_selected = False
        
        for i, button in enumerate(tank_select_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                selected_tank = i
                button.is_selected = True
        
        if selected_tank >= 0 and selected_tank < len(tank_select_buttons):
            tank_select_buttons[selected_tank].is_selected = True
        
        start_button.check_hover(mouse_pos)
        if start_button.is_clicked(mouse_pos, mouse_clicked):
            init_game()
            game_state = GAME
        
        back_button.check_hover(mouse_pos)
        if back_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = MAP_SELECT
    
    elif game_state == PAUSE:
        for button in pause_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Продолжить":
                    game_state = GAME
                elif button.text == "Выход":
                    game_state = MENU
    
    elif game_state == GAME_OVER:
        for button in game_over_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Заново":
                    init_game()
                    game_state = GAME
                elif button.text == "Выход":
                    game_state = MENU
    
    elif game_state == VICTORY:
        for button in victory_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button.text == "Заново":
                    init_game()
                    game_state = GAME
                elif button.text == "Выход":
                    game_state = MENU
    
    if game_state == GAME:
        for bullet in bullets: bullet.update()
        for obj in objects: obj.update()
    
    if game_state == MENU:
        draw_menu()
        draw_development()
    elif game_state == MAP_SELECT:
        draw_map_selection()
        draw_development()
    elif game_state == TANK_SELECT:
        draw_tank_selection()
        draw_development()
    elif game_state == GAME:
        window.blit(background, (0, 0))
        for bullet in bullets: bullet.draw()
        for obj in objects: obj.draw()
        draw_stats()
    elif game_state == PAUSE:
        window.fill(BLACK)
        for bullet in bullets: bullet.draw()
        for obj in objects: obj.draw()
        draw_stats()
        draw_pause()
    elif game_state == GAME_OVER:
        window.fill(BLACK)
        for bullet in bullets: bullet.draw()
        for obj in objects: obj.draw()
        draw_stats()
        draw_game_over()
    elif game_state == VICTORY:
        window.fill(BLACK)
        for bullet in bullets: bullet.draw()
        for obj in objects: obj.draw()
        draw_stats()
        draw_victory()
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()