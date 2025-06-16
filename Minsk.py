import pygame
import math
import sys
pygame.init()

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
TANK_SELECT = 1
GAME = 2
PAUSE = 3
GAME_OVER = 4
VICTORY = 5
game_state = MENU

#(0=Light, 1=Middle, 2=Heavy)
selected_tank = 1

#картинки
battlemap_1 = "img\\Minsk.jpg"
background = pygame.image.load(battlemap_1).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

menu_bg = pygame.image.load("img\\menu.png").convert()
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))

star_img = pygame.image.load('img/star.png').convert_alpha()
star_img = pygame.transform.scale(star_img, (20, 20))

victory_bg = pygame.image.load('img/victory_Minsk.png').convert()
victory_bg = pygame.transform.scale(victory_bg, (WIDTH, HEIGHT))

medal_img = pygame.image.load('img/medal.png').convert_alpha()
medal_img = pygame.transform.scale(medal_img, (140, 182.9))

#аудио
pygame.mixer.init(44100, -16, 2, 2048)
sound_map1 = "audio\Minsk.mp3"

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

IMPASSABLE_COLORS = ["2B3838", "3F4843"]
IMPENETRABLE_COLORS = ["000000"]

collision_mask = create_collision_mask(background, IMPASSABLE_COLORS)
impenetrable_mask = create_collision_mask(background, IMPENETRABLE_COLORS)


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
            self.hp = 5
            self.bulletDamage = 1

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
            self.hp = 5
            self.bulletDamage = 2            
        self.image = pygame.transform.scale(self.image, (TILE * 1.3, TILE * 1.3))        
        
class Heavy(Tank):
    def __init__(self, color, px, py, direct, keyList, is_enemy=False):
        super().__init__(color, px, py, direct, keyList, is_enemy)

        if is_enemy:
            self.image = pygame.image.load('img/tanks/h_g.png').convert_alpha()
            self.moveSpeed = 0.5
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

def draw_tank_selection():
    window.blit(menu_bg, (0, 0))
    title_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 40)
    title = title_font.render("ВЫБЕРИТЕ ТАНК", True, (55, 59, 56))
    window.blit(title, (WIDTH//2 - title.get_width()//2, 280))
    
    font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 20)
    
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
        window.blit(text, (20, 425 + i*25))
        
        if i > 0:
            for j in range(light_stars[i-1]):
                window.blit(star_img, (20 + text.get_width() + 10 + j*25, 425 + i*25))
    
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
        window.blit(text, (270, 425 + i*25))
        
        if i > 0:
            for j in range(middle_stars[i-1]):
                window.blit(star_img, (270 + text.get_width() + 10 + j*25, 425 + i*25))
    
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
        window.blit(text, (500, 425 + i*25))
        
        if i > 0:
            for j in range(heavy_stars[i-1]):
                window.blit(star_img, (500 + text.get_width() + 10 + j*25, 425 + i*25))
    
    for button in tank_select_buttons:
        button.draw(window)
    
    start_button.draw(window)

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
    window.blit(victory_bg, (0, 0))
    
    victory_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 50)
    text = victory_font.render("ПОБЕДА!", True, GREEN)
    window.blit(text, (WIDTH//2 - text.get_width()//2, 75))

    story_font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 18)
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
    
    max_text_width = max(story_font.size(line)[0] for line in story_lines)
    text_height = len(story_lines) * 30
    
    medal_width, medal_height = medal_img.get_size()
    
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
    content_surface.blit(medal_img, (medal_x, medal_y))
    
    content_x = (WIDTH - content_width) // 2
    content_y = 150
    window.blit(content_surface, (content_x, content_y))
    
    for button in victory_buttons:
        button.draw(window)

def init_game():
    global bullets, objects, enemies_killed, enemies_total
    
    bullets = []
    objects = []
    enemies_killed = 0
    
    enemy_positions = [
        (700, 100, 0),  #light
        (600, 300, 1),  #middle
        (700, 500, 2),  #heavy
        (400, 200, 0),
        (400, 400, 1)
    ]
    
    block_positions = []

    enemies_total = len(enemy_positions)

    pygame.mixer.music.load(sound_map1)
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1,0.0)    
    
    if selected_tank == 0:
        Light('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    elif selected_tank == 1:
        Middle('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    elif selected_tank == 2:
        Heavy('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    
    for x, y, tank_type in enemy_positions:
        if tank_type == 0:
            Light('red', x, y, 3, (), is_enemy=True)
        elif tank_type == 1:
            Middle('red', x, y, 3, (), is_enemy=True)
        elif tank_type == 2:
            Heavy('red', x, y, 3, (), is_enemy=True)
    
    for x, y in block_positions:
        Block(x, y, TILE)


menu_buttons = [
    Button(WIDTH//2 - 100, 350, 200, 50, "Играть", (94, 95, 64), (115, 109, 83)),
    Button(WIDTH//2 - 100, 420, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
]

tank_select_buttons = [
    Button(50, 350, 150, 50, "Легкий", (43, 56, 56), (63, 72, 67)),
    Button(300, 350, 150, 50, "Средний", (43, 56, 56), (63, 72, 67)),
    Button(535, 350, 150, 50, "Тяжелый", (43, 56, 56), (63, 72, 67))
]

start_button = Button(WIDTH//2 - 100, 600, 200, 50, "Начать игру", (81, 102, 58), (131, 163, 96))

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
                    game_state = TANK_SELECT
                elif button.text == "Выход":
                    running = False
    
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
    elif game_state == TANK_SELECT:
        draw_tank_selection()
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