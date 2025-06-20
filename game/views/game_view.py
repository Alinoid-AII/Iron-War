import pygame
import os
from ..models.game_state import GameState
from ..models.game_model import GameModel
from .button import Button
from ..models.tank import Tank

class GameView:
    def __init__(self, model):
        self.model = model
        self.WIDTH, self.HEIGHT = 750, 750
        self.TILE = 32
        self.init_colors()
        self.init_window()
        self.load_resources()
        self.init_buttons()

    def init_colors(self):
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (100, 100, 255)
        self.LIGHT_RED = (255, 100, 100)
        self.LIGHT_GREEN = (100, 255, 100)
        self.DEV_TRAPEZOID_COLOR = (200, 0, 0, 100)

    def init_window(self):
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("IRON WAR")
        self.clock = pygame.time.Clock()

    def load_resources(self):
        pygame.mixer.init(44100, -16, 2, 2048)
        self.shot_sound = pygame.mixer.Sound("resources/audio/shot.mp3")
        self.shot_sound.set_volume(0.3)
        
        self.star_img = pygame.image.load('resources/img/star.png').convert_alpha()
        self.star_img = pygame.transform.scale(self.star_img, (20, 20))
        
        self.medal_minsk = pygame.image.load('resources/img/medal.png').convert_alpha()
        self.medal_minsk = pygame.transform.scale(self.medal_minsk, (140, 182.9))
        self.medal_minsk_progress = pygame.image.load('resources/img/medal_minsk_pr.png').convert_alpha()
        self.medal_minsk_progress = pygame.transform.scale(self.medal_minsk_progress, (140, 202))
        self.medal_prokh = pygame.image.load('resources/img/medal_prokh.png').convert_alpha()
        self.medal_prokh = pygame.transform.scale(self.medal_prokh, (140, 206))
        
        self.tank_images = {
            "light": {
                "player": self.load_tank_image("resources\\img\\tanks\\l_u.png", "light"),
                "enemy": self.load_tank_image("resources\\img\\tanks\\l_g.png", "light")
            },
            "middle": {
                "player": self.load_tank_image("resources\\img\\tanks\\m_u.png", "middle"),
                "enemy": self.load_tank_image("resources\\img\\tanks\\m_g.png", "middle")
            },
            "heavy": {
                "player": self.load_tank_image("resources\\img\\tanks\\h_u.png", "heavy"),
                "enemy": self.load_tank_image("resources\\img\\tanks\\h_g.png", "heavy")
            }
        }
        
        for map_data in self.model.maps:
            background = pygame.image.load(map_data.get("background", "resources\img\Minsk.jpg")).convert()
            background = pygame.transform.scale(background, (self.WIDTH, self.HEIGHT))
            map_data["scaled_background"] = background
            
            victory_bg = pygame.image.load(map_data.get("victory_bg", "resources\\img\\victory_Minsk.png")).convert()
            victory_bg = pygame.transform.scale(victory_bg, (self.WIDTH, self.HEIGHT))
            map_data["scaled_victory_bg"] = victory_bg
            
            menu_bg = pygame.image.load(map_data.get("menu_bg", "resources\\img\\menu.png")).convert()
            menu_bg = pygame.transform.scale(menu_bg, (self.WIDTH, self.HEIGHT))
            map_data["scaled_menu_bg"] = menu_bg
            
            map_data["collision_mask"] = self.model.create_collision_mask(
                map_data["scaled_background"], map_data["impassable_colors"])
            map_data["impenetrable_mask"] = self.model.create_collision_mask(
                map_data["scaled_background"], map_data["impenetrable_colors"])

    def load_tank_image(self, path, tank_type):
        image = pygame.image.load(path).convert_alpha()
        scale = Tank.TANK_STATS[tank_type]["scale"]
        return pygame.transform.scale(image, (self.TILE * scale, self.TILE * scale))

    def init_buttons(self):
        self.menu_buttons = [
            Button(self.WIDTH//2 - 100, 350, 200, 50, "Играть", (94, 95, 64), (115, 109, 83)),
            Button(self.WIDTH//2 - 100, 420, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
        ]
        
        self.map_select_buttons = [
            Button(self.WIDTH//2 - 200, 300, 180, 50, "Минск", (43, 56, 56), (63, 72, 67)),
            Button(self.WIDTH//2 + 20, 300, 180, 50, "Прохоровка", (43, 56, 56), (63, 72, 67))
        ]
        
        self.back_button = Button(self.WIDTH//2 - 100, 500, 200, 50, "Назад", (148, 47, 61), (204, 92, 107))
        
        self.tank_select_buttons = [
            Button(50, 270, 150, 50, "Легкий", (43, 56, 56), (63, 72, 67)),
            Button(300, 270, 150, 50, "Средний", (43, 56, 56), (63, 72, 67)),
            Button(535, 270, 150, 50, "Тяжелый", (43, 56, 56), (63, 72, 67))
        ]
        
        self.start_button = Button(self.WIDTH//2 - 100, 570, 200, 50, "Начать игру", (81, 102, 58), (131, 163, 96))
        
        self.pause_buttons = [
            Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 10, 200, 50, "Продолжить", (81, 102, 58), (131, 163, 96)),
            Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 80, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
        ]
        
        self.game_over_buttons = [
            Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 10, 200, 50, "Заново", (81, 102, 58), (131, 163, 96)),
            Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 80, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
        ]
        
        self.victory_buttons = [
            Button(self.WIDTH//2 - 100, self.HEIGHT - 160, 200, 50, "Заново", (81, 102, 58), (131, 163, 96)),
            Button(self.WIDTH//2 - 100, self.HEIGHT - 90, 200, 50, "Выход", (148, 47, 61), (204, 92, 107))
        ]

    def draw(self):
        if self.model.state == GameState.MENU:
            self.draw_menu()
        elif self.model.state == GameState.MAP_SELECT:
            self.draw_map_selection()
        elif self.model.state == GameState.TANK_SELECT:
            self.draw_tank_selection()
        elif self.model.state == GameState.GAME:
            self.draw_game()
        elif self.model.state == GameState.PAUSE:
            self.draw_game()
            self.draw_pause()
        elif self.model.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.model.state == GameState.VICTORY:
            self.draw_victory()
        
        pygame.display.update()
        self.clock.tick(60)

    def draw_menu(self):
        map_data = self.model.maps[self.model.selected_map]
        self.window.blit(map_data["scaled_menu_bg"], (0, 0))
        for button in self.menu_buttons:
            button.draw(self.window)
        self.draw_development()

    def draw_map_selection(self):
        map_data = self.model.maps[self.model.selected_map]
        self.window.blit(map_data["scaled_menu_bg"], (0, 0))
        
        title_font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 40)
        title = title_font.render("ВЫБЕРИТЕ КАРТУ", True, (55, 59, 56))
        self.window.blit(title, (self.WIDTH//2 - title.get_width()//2, 200))
        
        for button in self.map_select_buttons:
            button.draw(self.window)
        
        if self.model.progress["completed_minsk"]:
            self.window.blit(self.medal_minsk_progress, (20, 300))
        if self.model.progress["completed_prokh"]:
            self.window.blit(self.medal_prokh, (self.WIDTH//2 + 20 + 180 + 10, 300))
        
        self.back_button.draw(self.window)
        self.draw_development()

    def draw_tank_selection(self):
        map_data = self.model.maps[self.model.selected_map]
        self.window.blit(map_data["scaled_menu_bg"], (0, 0))
        title_font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 40)
        title = title_font.render("ВЫБЕРИТЕ ТАНК", True, (55, 59, 56))
        self.window.blit(title, (self.WIDTH//2 - title.get_width()//2, 200))
        
        font = pygame.font.Font("resources/fonts/Montserrat-Bold.ttf", 20)
        light_stats = font.render(f"Побед: {self.model.progress['light_tank_wins']}", True, (43, 56, 56))
        middle_stats = font.render(f"Побед: {self.model.progress['middle_tank_wins']}", True, (43, 56, 56))    
        heavy_stats = font.render(f"Побед: {self.model.progress['heavy_tank_wins']}", True, (43, 56, 56))
        self.window.blit(light_stats, (70, 330))
        self.window.blit(middle_stats, (325, 330))
        self.window.blit(heavy_stats, (560, 330))
        
        self.draw_tank_stats("light", 20, 360, [5, 3, 1])
        self.draw_tank_stats("middle", 270, 360, [3, 4, 2])
        self.draw_tank_stats("heavy", 500, 360, [1, 5, 3])
        
        for button in self.tank_select_buttons:
            button.draw(self.window)
        
        self.start_button.draw(self.window)
        self.back_button.draw(self.window)
        self.draw_development()

    def draw_tank_stats(self, tank_type, x, y, stats):
        desc = [
            "ЛЕГКИЙ ТАНК" if tank_type == "light" else 
            "СРЕДНИЙ ТАНК" if tank_type == "middle" else "ТЯЖЕЛЫЙ ТАНК",
            "Скорость:",
            "Здоровье:",
            "Урон:"
        ]
        font = pygame.font.Font("resources/fonts/Montserrat-Bold.ttf", 20)
        
        for i, line in enumerate(desc):
            text = font.render(line, True, (43, 56, 56))
            self.window.blit(text, (x, y + i*25))
            if i > 0:
                for j in range(stats[i-1]):
                    self.window.blit(self.star_img, (x + text.get_width() + 10 + j*25, y + i*25))

    def draw_game(self):
        map_data = self.model.maps[self.model.selected_map]
        self.window.blit(map_data["scaled_background"], (0, 0))
        
        for bullet in self.model.get_bullets():
            pygame.draw.circle(self.window, self.YELLOW, (int(bullet.px), int(bullet.py)), bullet.radius)
        
        for obj in self.model.get_objects():
            if isinstance(obj, Tank):
                image = self.tank_images[obj.tank_type]["enemy" if obj.is_enemy else "player"]
                rotated_image = pygame.transform.rotate(image, -obj.direct * 90)
                self.window.blit(rotated_image, obj.rect)
        
        self.draw_stats()

    def draw_stats(self):
        font = pygame.font.Font("resources/fonts/Montserrat-Bold.ttf", 24)
        enemies_text = font.render(f"Уничтожено: {self.model.enemies_killed}/{self.model.enemies_total}", True, self.WHITE)
        self.window.blit(enemies_text, (10, 10))
        
        player = None
        for obj in self.model.get_objects():
            if isinstance(obj, Tank) and not obj.is_enemy:
                player = obj
                break
        if player:
            health_text = font.render(f"Здоровье: {player.hp}", True, self.WHITE)
            self.window.blit(health_text, (10, 40))

    def draw_pause(self):
        s = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.window.blit(s, (0, 0))
        
        pause_font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 50)
        pause_text = pause_font.render("ПАУЗА", True, self.WHITE)
        self.window.blit(pause_text, (self.WIDTH//2 - pause_text.get_width()//2, self.HEIGHT//2 - 80))
        
        for button in self.pause_buttons:
            button.draw(self.window)

    def draw_game_over(self):
        s = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.window.blit(s, (0, 0))
        
        font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 50)
        text = font.render("ПОРАЖЕНИЕ", True, self.RED)
        self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, self.HEIGHT//2 - 80))
        
        for button in self.game_over_buttons:
            button.draw(self.window)

    def draw_victory(self):
        map_data = self.model.maps[self.model.selected_map]
        self.window.blit(map_data["scaled_victory_bg"], (0, 0))
        
        victory_font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 50)
        text = victory_font.render("ПОБЕДА!", True, self.GREEN)
        self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, 75))

        story_font = pygame.font.Font("resources/fonts/Montserrat-Bold.ttf", 18)
        story_lines, medal = self.get_victory_content()
        
        max_text_width = max(story_font.size(line)[0] for line in story_lines)
        text_height = len(story_lines) * 30
        medal_width, medal_height = medal.get_size()
        
        content_width = max_text_width + medal_width + 60
        content_height = max(text_height, medal_height) + 40
        
        content_surface = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
        content_surface.fill((0, 0, 0, 150))
        
        story_x = 20
        story_y = 20
        for i, line in enumerate(story_lines):
            text_surface = story_font.render(line, True, self.WHITE)
            content_surface.blit(text_surface, (story_x, story_y + i*30))
        
        medal_x = content_width - medal_width - 20
        medal_y = 20
        content_surface.blit(medal, (medal_x, medal_y))
        
        content_x = (self.WIDTH - content_width) // 2
        content_y = 150
        self.window.blit(content_surface, (content_x, content_y))
        
        for button in self.victory_buttons:
            button.draw(self.window)

    def get_victory_content(self):
        if self.model.selected_map == 0:
            return [
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
            ], self.medal_minsk
        else:
            return [
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
            ], self.medal_prokh

    def draw_development(self):
        base_width = 300
        top_width = 200
        trapezoid_height = 40
        surf_size = max(base_width, trapezoid_height) * 2
        development_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        left_offset = (base_width - top_width) // 2
        points = [
            (left_offset, surf_size//2 - trapezoid_height//2),
            (left_offset + top_width, surf_size//2 - trapezoid_height//2),
            (base_width, surf_size//2 + trapezoid_height//2),
            (0, surf_size//2 + trapezoid_height//2)
        ]
        pygame.draw.polygon(development_surf, self.DEV_TRAPEZOID_COLOR, points)
        font = pygame.font.Font("resources/fonts/Montserrat-Bold.ttf", 18)
        text = font.render("Development", True, self.WHITE)
        text_rect = text.get_rect(center=(base_width//2, surf_size//2))
        development_surf.blit(text, text_rect)
        rotated_surf = pygame.transform.rotate(development_surf, 45)
        offset_x = -rotated_surf.get_width() // 3.65
        offset_y = -rotated_surf.get_height() // 1.9
        self.window.blit(rotated_surf, (offset_x, offset_y))